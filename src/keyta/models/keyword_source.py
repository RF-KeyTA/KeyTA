import json
import re
import tempfile
from abc import abstractmethod
from pathlib import Path
from typing import TypedDict

from jinja2 import Template
from robot.libdoc import libdoc

from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from keyta.apps.keywords.models import (
    Keyword,
    KeywordParameter,
    KeywordReturnValue
)

from .base_model import AbstractBaseModel


class TypeDoc(TypedDict):
    name: str
    doc: str
    items: list[str]
    type: str


def args_table(libdoc_args: list[dict], typedocs: dict[str, TypeDoc]):
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


def format_return_type(return_type: list, typedocs: dict[str, TypeDoc]) -> str:
    if not return_type:
        return ''

    template = """
    {{ type_repr }}
    {% for typedoc in typedocs %}
    <div id="{{ typedoc.name }}" class="modal" tabindex="-1" role="dialog">
        {{ typedoc.doc }}
    </div>
    {% endfor %}
    """

    return_typedocs = []
    for type_ in return_type:
        if isinstance(type_, list):
            list_type = type_[0]
            if list_type in typedocs:
                return_typedocs.append(typedocs[list_type])
        else:
            if type_ in typedocs:
                return_typedocs.append(typedocs[type_])

    return Template(template).render({
        'type_repr': format_type(return_type, typedocs),
        'typedocs': return_typedocs
    }).strip()


def format_type(type: list, typedocs: dict[str, TypeDoc]) -> str:
    formatted_type = []

    if type and type[0] == 'Literal':
        Literal, *values = type
        return " | ".join(values)

    for type_ in type:
        if isinstance(type_, list):
            list_type = type_[0]
            if list_type in typedocs:
                formatted_type.append(f'list[<a href="#{list_type}" onclick="bsShowModal(\'#{list_type}\')">{list_type}</a>]')
            else:
                formatted_type.append(f'list[{list_type}]')
        elif type_ in typedocs:
            formatted_type.append(f'<a href="#{type_}" onclick="bsShowModal(\'#{type_}\')">{type_}</a>')
        else:
            formatted_type.append(str(type_))

    return " | ".join(formatted_type)


def get_default_value(default_value):
    if default_value is None or default_value == 'None':
        return '${None}'

    if default_value == '':
        return '${EMPTY}'

    return default_value


def get_init_doc(library_json):
    if library_json["inits"]:
        return library_json["inits"][0]["doc"]
    else:
        return _("Diese Bibliothek hat keine Einstellungen")


def get_libdoc_dict(library_or_resource: str) -> dict:
    libdoc_json = Path(tempfile.gettempdir()) / f"{library_or_resource}.json"
    libdoc(library_or_resource, str(libdoc_json))

    with open(libdoc_json, encoding='utf-8') as file:
        return json.load(file)


def get_return_type(return_type: dict | None) -> list:
    if return_type is None:
        return []

    if return_type['union']:
        types = []

        for type_ in return_type['nested']:
            typedoc = type_['typedoc']

            if typedoc == 'list':
                if nested := type_['nested']:
                    types.append([nested[0]['name']])
                else:
                    types.append('list')
            else:
                types.append(type_['name'])

        return types
    else:
        name = return_type['name']

        if name == 'dict':
            types = [name]
        else:
            typedoc = return_type['typedoc']

            if typedoc is None:
                return []

            types = [typedoc]

            if typedoc == 'list':
                if nested := return_type['nested']:
                    types = [[nested[0]['name']]]
                else:
                    types = ['list']

        return types


def get_type(arg: dict) -> list[str]:
    if isinstance(arg['type'], dict) and arg['type']['name'] == 'Literal':
        return ['Literal'] + [
            value['name'].replace("'", "").replace('"', '')
            for value in arg['type']['nested']
        ]

    type_hint_regex = re.compile(r"[*]*\w+: ([\w|\[\]\s,']+)")

    if type_hint := type_hint_regex.match(arg['repr']):
        union_type = type_hint.group(1).split('|')
        return [
            member_type.strip()
            for member_type in union_type
        ]

    return []


def get_typedocs(libdoc_typedocs: list[dict]) -> dict[str, TypeDoc]:
    typedocs = dict()

    for typedoc in libdoc_typedocs:
        name = typedoc['name']
        type_ = typedoc['type']

        if type_ == 'Enum':
            typedocs[name] = TypeDoc(
                name=name,
                doc=typedoc['doc'],
                items=[
                    member['name']
                    for member in typedoc['members']
                ],
                type=type_
            )
        elif type_ == 'TypedDict':
            typedocs[name] = TypeDoc(
                name=name,
                doc=typedoc['doc'],
                items=[
                    item['key']
                    for item in typedoc['items']
                ],
                type=type_
            )
        else:
            typedocs[name] = TypeDoc(
                name=name,
                doc=typedoc['doc'],
                items=[],
                type=type_
            )

    return typedocs


def heading(title: str):
    return f"""
    <div class="row">
        <label class="col-sm-6 text-left">
            {title}
        </label>
    </div>
    """


def return_type_doc(return_type: list, typedocs: dict[str, TypeDoc]) -> str:
    if not return_type:
        return ''

    return heading(_('Rückgabetyp')) + format_return_type(return_type, typedocs) + '<div class="mb-4"></div>'


def section_importing(libdoc_dict: dict):
    if libdoc_dict["inits"]:
        return '<h2 id="Importing">Importing</h2>' + get_init_doc(libdoc_dict)

    return ''


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

    def import_keywords(self, libdoc_dict: dict, typedocs: dict[str, TypeDoc]):
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

            return_type = get_return_type(keyword['returnType'])

            kw, created = Keyword.objects.update_or_create(**{
                **kw_args,
                'name': name,
                'defaults': {
                    'documentation': (
                        args_table(keyword['args'], typedocs) +
                        return_type_doc(return_type, typedocs) +
                        heading(_('Dokumentation')) + keyword['doc']
                    ),
                    'short_doc': keyword['shortdoc']
                }
            })

            if return_type:
                return_value, created = KeywordReturnValue.objects.update_or_create(
                    keyword=kw,
                    defaults={
                        'type': format_return_type(return_type, typedocs)
                    }
                )

                for type_ in return_type:
                    if isinstance(type_, str) and type_ in typedocs:
                        typedoc = typedocs[type_]
                        if typedoc['type'] == 'TypedDict':
                            return_value.set_typedoc({
                                'name': typedoc['name'],
                                'keys': typedoc['items']
                            })
                        break

            kwarg_names = set()
            kw_args = [arg for arg in keyword['args'] if arg['name']]

            for idx, arg, in enumerate(kw_args):
                name = arg["name"]
                kind = arg['kind']

                if arg["required"]:
                    KeywordParameter.create_arg(
                        keyword=kw,
                        name=name,
                        kind=kind,
                        position=idx,
                        typedoc=get_type(arg)
                    )
                else:
                    if kind in {'VAR_NAMED', 'VAR_POSITIONAL'}:
                        if kind == 'VAR_NAMED':
                            KeywordParameter.create_varkwarg(
                                keyword=kw,
                                name=name,
                                kind=kind,
                                position=idx,
                                typedoc=get_type(arg)
                            )

                        if kind == 'VAR_POSITIONAL':
                            KeywordParameter.create_vararg(
                                keyword=kw,
                                name=name,
                                kind=kind,
                                position=idx,
                                typedoc=get_type(arg)
                            )
                    else:
                        kwarg_names.add(name)
                        default_value = get_default_value(arg["defaultValue"])
                        KeywordParameter.create_kwarg(
                            keyword=kw,
                            name=name,
                            default_value=default_value,
                            kind=kind,
                            position=idx,
                            typedoc=get_type(arg)
                        )

            for kwarg in kw.parameters.kwargs():
                if kwarg.name not in kwarg_names:
                    kwarg.delete()

            if not return_type:
                for return_value in kw.return_values.all():
                    return_value.delete()

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
