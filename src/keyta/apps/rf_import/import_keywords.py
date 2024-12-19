import json
import os
import re
import tempfile
import urllib.parse
import xml.dom.minidom
from pathlib import Path

from django.utils.translation import gettext as _

from apps.common.widgets import open_link_in_modal
from apps.keywords.models import Keyword, KeywordParameter, KeywordType
from apps.libraries.models import Library
from apps.resources.models import Resource


def get_libdoc_json(library_or_resource: str):
    libdoc_json = Path(tempfile.gettempdir()) / f"{library_or_resource}.json"
    os.system(f'libdoc {library_or_resource} {libdoc_json}')

    with open(libdoc_json, encoding='utf-8') as file:
        return json.load(file)


def import_keywords(libdoc_json, library_or_resource):
    keyword_names = set()
    deprecated_keywords = set()

    for keyword in libdoc_json["keywords"]:
        name = keyword["name"]

        if keyword.get('deprecated', False):
            deprecated_keywords.add(name)
            continue

        keyword_names.add(name)

        if isinstance(library_or_resource, Library):
            kw, created = Keyword.objects.update_or_create(
                library=library_or_resource,
                type=KeywordType.LIBRARY,
                name=name,
                defaults={
                    'args_doc': args_table(keyword["args"]),
                    'documentation': keyword["doc"],
                    'short_doc': keyword['shortdoc']
                }
            )

        if isinstance(library_or_resource, Resource):
            kw, created = Keyword.objects.update_or_create(
                resource=library_or_resource,
                type=KeywordType.RESOURCE,
                name=name,
                defaults={
                    'args_doc': args_table(keyword["args"]),
                    'documentation': keyword["doc"],
                    'short_doc': keyword['shortdoc']
                }
            )

        kwarg_names = set()
        for idx, arg, in enumerate(keyword["args"]):
            name = arg["name"]
            if not name:
                continue

            if arg["required"]:
                KeywordParameter.create_arg(
                    keyword=kw,
                    name=name,
                    position=idx
                )
            else:
                if arg["kind"] == 'VAR_POSITIONAL':
                    KeywordParameter.create_arg(
                        keyword=kw,
                        name=name,
                        position=idx,
                        is_list=True
                    )
                else:
                    kwarg_names.add(name)
                    default_value = get_default_value(
                        arg["defaultValue"],
                        arg["kind"]
                    )
                    KeywordParameter.create_kwarg(
                        keyword=kw,
                        name=name,
                        default_value=default_value
                    )

        for kwarg in kw.parameters.kwargs():
            if kwarg.name not in kwarg_names:
                kwarg.delete()

    keyword: Keyword
    for keyword in library_or_resource.keywords.all():
        if ((keyword.name in deprecated_keywords or
             keyword.name not in keyword_names) and
                not keyword.uses.exists()):
            keyword.delete()

    library_or_resource.documentation = replace_links(library_or_resource.documentation, library_or_resource, heading_links=False)
    library_or_resource.save()

    for lib_keyword in library_or_resource.keywords.all():
        lib_keyword.documentation = replace_links(lib_keyword.documentation, library_or_resource)
        lib_keyword.save()


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
    <p></p>
    """


def get_default_value(default_value, kind):
    if default_value is None or default_value == 'None':
        return '${None}'

    if default_value == '':
        return '${EMPTY}'

    return default_value


def replace_links(docstring: str, library_or_resource, heading_links=True):
    heading_ids = set(re.findall(r'<h\d id=\"([^"]*)\"', library_or_resource.documentation))

    def replace_link(match: re.Match):
        link_str = match.group(0)
        link = xml.dom.minidom.parseString(link_str).getElementsByTagName('a')[0]
        href: str = link.attributes['href'].value
        text: str = link.firstChild.nodeValue

        if href.startswith('http'):
            link.attributes['target'] = '_blank'
            return link.toxml()

        if href.startswith('#'):
            if keyword := Keyword.objects.filter(library=library_or_resource, name__iexact=text).first():
                return open_link_in_modal(keyword.get_docadmin_url(), keyword.name)

            if heading_links and urllib.parse.unquote(href.lstrip('#')) in heading_ids:
                link.attributes['href'] = library_or_resource.get_admin_url() + href
                link.attributes['target'] = '_blank'
                return link.toxml()

        return link.toxml()

    return re.sub(
        r'<a[^>]*>[^<]*</a>',
        replace_link,
        docstring
    )


def get_init_doc(library_json):
    if library_json["inits"]:
        return library_json["inits"][0]["doc"]
    else:
        return _("Diese Bibliothek hat keine Einstellungen")


def section_importing(lib_json: dict):
    if lib_json["inits"]:
        return '<h2 id="Importing">Importing</h2>\n' + get_init_doc(lib_json)

    return ''
