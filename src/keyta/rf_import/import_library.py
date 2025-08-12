import json

from keyta.apps.libraries.models import Library, LibraryParameter

from .import_keywords import (
    get_default_value,
    get_init_doc,
    section_importing
)


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


def import_library(libdoc_dict: dict):
    typedocs = get_typedocs(libdoc_dict['typedocs'])
    lib: Library
    lib, created = Library.objects.update_or_create(
        name=libdoc_dict["name"],
        defaults={
            'version': libdoc_dict["version"],
            'init_doc': get_init_doc(libdoc_dict),
            'documentation': libdoc_dict["doc"] + section_importing(libdoc_dict),
            'typedocs': json.dumps(typedocs)
        }
    )

    if libdoc_dict["inits"]:
        init_args = libdoc_dict["inits"][0]["args"]
        init_args_names = set()

        for init_arg in init_args:
            name = init_arg["name"]

            if name == '_':
                continue

            init_args_names.add(name)
            default_value = get_default_value(init_arg["defaultValue"])

            LibraryParameter.objects.get_or_create(
                library=lib,
                name=name,
                defaults={
                    'default_value': default_value
                }
            )

        for init_arg in lib.kwargs.all():
            if init_arg.name not in init_args_names:
                init_arg.delete()

    lib.import_keywords(libdoc_dict, typedocs)

    return lib
