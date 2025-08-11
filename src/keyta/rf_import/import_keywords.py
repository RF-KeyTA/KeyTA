import json
import os
import re
import tempfile
from pathlib import Path

from django.utils.translation import gettext_lazy as _
from jinja2 import Template


def args_table(libdoc_args: list[dict], typedocs: dict[str, dict]):
    if not libdoc_args:
        return ""

    template = """
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
    <script>
        function bsShowModal(selector) {
            let content = document.querySelector(selector)
            let modal_selector = '.modal-body ' + selector
            $.showModal({
                title: selector.replace('#', ''), 
                body: content.outerHTML, 
                backdrop: false, 
                modalDialogClass: "modal-dialog-centered modal-lg", 
                modalClass: "fade modal-wide related-modal-2"
            })
            let modal = document.querySelector(modal_selector)
            modal.classList.remove('modal')
        }
    </script>
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


def format_type(arg_type: list, typedocs: dict[str, dict]):
    formatted_type = []

    for type_ in arg_type:
        if type_ in typedocs:
            formatted_type.append(f'<a href="#{type_}" onclick="bsShowModal(\'#{type_}\')">{type_}</a>')
        else:
            formatted_type.append(type_)

    return " | ".join(formatted_type)


def get_default_value(default_value, kind):
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


def get_libdoc_dict(library_or_resource: str) -> dict:
    libdoc_json = Path(tempfile.gettempdir()) / f"{library_or_resource}.json"
    os.system(f'libdoc "{library_or_resource}" "{libdoc_json}"')

    with open(libdoc_json, encoding='utf-8') as file:
        return json.load(file)


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


def section_importing(lib_json: dict):
    if lib_json["inits"]:
        return '<h2 id="Importing">Importing</h2>\n' + get_init_doc(lib_json)

    return ''
