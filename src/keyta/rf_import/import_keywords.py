import json
import os
import tempfile
from pathlib import Path

from django.utils.translation import gettext_lazy as _


def args_table(args):
    if not args:
        return ""

    newline = "\n"
    return f"""
    <table cellpadding="3">
    {newline.join([
        f'<tr><td>{format_arg(arg)}</td><td>{"=" if format_default_value(arg) else ""}</td><td>{format_default_value(arg)}</td></tr>'
        for arg in args
    ])}
    </table>
    """


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


def get_default_value(default_value, kind):
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


def get_libdoc_json(library_or_resource: str):
    libdoc_json = Path(tempfile.gettempdir()) / f"{library_or_resource}.json"
    os.system(f'libdoc "{library_or_resource}" "{libdoc_json}"')

    with open(libdoc_json, encoding='utf-8') as file:
        return json.load(file)


def section_importing(lib_json: dict):
    if lib_json["inits"]:
        return '<h2 id="Importing">Importing</h2>\n' + get_init_doc(lib_json)

    return ''
