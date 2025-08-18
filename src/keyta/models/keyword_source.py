import json
import os
import re
import subprocess
import tempfile
from abc import abstractmethod
from pathlib import Path

from jinja2 import Template

from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from keyta.apps.keywords.models import (
    Keyword,
    KeywordParameter,
    KeywordReturnValue
)

from .base_model import AbstractBaseModel


def args_table(libdoc_args: list[dict], typedocs: dict[str, dict]):
    if not libdoc_args:
        return ''

    template = heading(_('Parameters')) + """
    <table class="table table-borderless table-sm">
        <thead>
            <tr>
                <th scope="col" style="width: 33.3%">Name</th>
                <th scope="col" style="width: 33.3%">Default</th>
                <th scope="col" style="width: 33.3%">Type</th>
            </tr>
        </thead>
        {% for arg in args %}
        <tr>
            <td>{{ arg.name }}</td>
            <td>{% if arg.default_value %}{{ arg.default_value }}{% endif %}</td>
            <td>{{ arg.type }}</td>
        </tr>
        {% endfor %}
    </table>

    {% for typedoc in typedocs %}
    <div id="{{ typedoc.name }}" class="modal" tabindex="-1" role="dialog">
        {{ typedoc.doc }}
    </div>
    {% endfor %}
    """

    args = []
    arg_types = set()

    for arg in libdoc_args:
        if arg['name']:
            arg_type = get_type(arg)
            arg_types.update(arg_type)
            args.append(
                {
                    'name': format_arg(arg),
                    'default_value': format_default_value(arg),
                    'type': format_type(arg_type, typedocs)
                }
            )

    arg_typedocs = [
        typedoc
        for type_ in arg_types
        if (typedoc := typedocs.get(type_))
    ]

    return Template(template).render({
        'args': args,
        'typedocs': arg_typedocs
    })


def format_arg(arg: dict):
    prefix = ""

    if arg["kind"] == "VAR_POSITIONAL":
        prefix = "*"

    if arg["kind"] == "VAR_NAMED":
        prefix = "**"

    return prefix + arg["name"]


def format_default_value(arg: dict):
    if not arg["required"] and not (arg["kind"] == "VAR_POSITIONAL" or arg["kind"] == "VAR_NAMED"):
        return arg["defaultValue"]

    return ""


def format_return_type(return_type: dict | None, typedocs: dict[str, dict]):
    if not return_type:
        return ''

    if return_type['union']:
        types = []

        for type_ in return_type['nested']:
            typedoc = type_['typedoc']

            if typedoc == 'list':
                if nested := type_['nested']:
                    types.append('list[%s]' % nested[0]['name'])
                else:
                    types.append('list')
            else:
                types.append(type_['name'])
    else:
        name = return_type['name']

        if name in {'dict'}:
            types = [name]
        else:
            typedoc = return_type['typedoc']
            types = [typedoc]

            if typedoc == 'list':
                if nested := return_type['nested']:
                    types = ['list[%s]' % nested[0]['name']]
                else:
                    types = ['list']

    template = heading(_('Rückgabetyp')) + """
    <div class="mb-4">
        <p>{{ type_repr }}</p>
    </div>
    {% for typedoc in typedocs %}
    <div id="{{ typedoc.name }}" class="modal" tabindex="-1" role="dialog">
        {{ typedoc.doc }}
    </div>
    {% endfor %}
    """

    return_typedocs = [
        typedoc
        for type_ in types
        if (typedoc := typedocs.get(type_))
    ]

    return Template(template).render({
        'type_repr': format_type(types, typedocs),
        'typedocs': return_typedocs
    })


def format_type(arg_type: list, typedocs: dict[str, dict]):
    formatted_type = []

    for type_ in arg_type:
        if type_ in typedocs:
            formatted_type.append(f'<a href="#{type_}" onclick="bsShowModal(\'#{type_}\')">{type_}</a>')
        else:
            if type_ is None:
                formatted_type.append('None')
            else:
                formatted_type.append(type_)

    return " | ".join(formatted_type)


def get_default_value(default_value):
    if default_value is None or default_value == 'None':
        return 'None'

    if default_value == '':
        return '${EMPTY}'

    return default_value


def get_init_doc(library_json):
    if library_json["inits"]:
        return library_json["inits"][0]["doc"]
    else:
        return _("Diese Bibliothek hat keine Einstellungen")


def get_type(arg: dict) -> list[str]:
    type_hint_regex = re.compile(r'[*]*\w+: ([\w|\[\]\s,]+)')

    if type_hint := type_hint_regex.match(arg['repr']):
        union_type = type_hint.group(1).split('|')
        type = [
            member_type.strip()
            for member_type in union_type
        ]
    else:
        type = []

    return type


def heading(title: str):
    return f"""
    <div class="row">
        <label class="col-sm-6 text-left">
            {title}
        </label>
    </div>
    """


def section_importing(lib_json: dict):
    if lib_json["inits"]:
        return '<h2 id="Importing">Importing</h2>\n' + get_init_doc(lib_json)

    return ''


def get_libdoc_dict(library_or_resource: str) -> dict:
    libdoc_json = Path(tempfile.gettempdir()) / f"{library_or_resource}.json"
    libdoc = subprocess.run(
        f'libdoc "{library_or_resource}" "{libdoc_json}"',
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    if libdoc.returncode == 0:
        with open(libdoc_json, encoding='utf-8') as file:
            return json.load(file)

    raise Exception(libdoc.stdout.decode('utf-8'))


def get_typedocs(libdoc_typedocs: list[dict]) -> dict[str, dict]:
    typedocs = dict()

    for typedoc in libdoc_typedocs:
        name = typedoc['name']

        if typedoc['type'] == 'Enum':
            typedocs[name] = {
                'type': 'Enum',
                'name': name,
                'doc': typedoc['doc'],
                'members': [
                    member['name']
                    for member in typedoc['members']
                ]
            }

        if typedoc['type'] == 'TypedDict':
            typedocs[name] = {
                'type': 'TypedDict',
                'name': name,
                'doc': typedoc['doc'],
                'keys': [
                    item['key']
                    for item in typedoc['items']
                ]
            }

    return typedocs


class KeywordSource(AbstractBaseModel):
    name = models.CharField(
        max_length=255, 
        verbose_name=_('Name')
    )
    documentation = models.TextField(
        verbose_name=_('Dokumentation')
    )

    def __str__(self):
        return self.name

    def import_keywords(self, libdoc_dict: dict, typedocs: dict[str, dict]):
        keyword_names = set()
        deprecated_keywords = set()

        keyword: dict
        for keyword in libdoc_dict["keywords"]:
            name = keyword["name"]

            if keyword.get('deprecated', False):
                deprecated_keywords.add(name)
                continue

            keyword_names.add(name)

            kw_args = {}

            if self.is_library():
                kw_args['library'] = self
            else:
                kw_args['resource'] = self

            kw, created = Keyword.objects.update_or_create(**{
                **kw_args,
                'name': name,
                'defaults': {
                    'documentation': (
                        args_table(keyword['args'], typedocs) +
                        format_return_type(keyword['returnType'], typedocs) +
                        heading(_('Dokumentation')) +
                        keyword['doc']
                    ),
                    'short_doc': keyword['shortdoc']
                }
            })

            kwarg_names = set()
            for idx, arg, in enumerate(keyword["args"]):
                name = arg["name"]
                if not name:
                    continue

                if arg["required"]:
                    KeywordParameter.create_arg(
                        keyword=kw,
                        name=name,
                        position=idx,
                        typedoc=json.dumps(get_type(arg))
                    )
                else:
                    if arg["kind"] == 'VAR_POSITIONAL':
                        KeywordParameter.create_vararg(
                            keyword=kw,
                            name=name,
                            position=idx,
                            typedoc=json.dumps(get_type(arg))
                        )
                    else:
                        kwarg_names.add(name)
                        default_value = get_default_value(arg["defaultValue"])
                        KeywordParameter.create_kwarg(
                            keyword=kw,
                            name=name,
                            default_value=default_value,
                            position=idx,
                            typedoc=json.dumps(get_type(arg))
                        )

            for kwarg in kw.parameters.kwargs():
                if kwarg.name not in kwarg_names:
                    kwarg.delete()

            if keyword.get('returnType'):
                for typedoc in libdoc_dict['typedocs']:
                    if (
                        typedoc['name'] == keyword['returnType']['typedoc'] and
                        typedoc['type'] == 'TypedDict'
                    ):
                        KeywordReturnValue.objects.update_or_create(
                            keyword=kw,
                            typedoc=json.dumps({
                                'name': typedoc['name'],
                                'type': 'dict',
                                'keys': [
                                    item['key']
                                    for item in typedoc['items']
                                ]
                            })
                        )

        for kw in self.keywords.all():
            if (
                (kw.name in deprecated_keywords or kw.name not in keyword_names)
                and not kw.uses.exists()
            ):
                kw.delete()
                continue

    @abstractmethod
    def is_library(self) -> bool:
        pass

    class Meta:
        abstract = True
        ordering = [Lower('name')]
