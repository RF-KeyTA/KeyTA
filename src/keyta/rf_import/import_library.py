import json

from keyta.apps.libraries.models import Library, LibraryParameter
from keyta.models.keyword_source import (
    get_default_value,
    get_init_doc,
    get_libdoc_dict,
    get_type,
    get_typedocs,
    section_importing
)


def import_library(name: str):
    libdoc_dict = get_libdoc_dict(name)
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

            LibraryParameter.objects.update_or_create(
                library=lib,
                name=name,
                defaults={
                    'orig_default_value': default_value,
                    'typedoc': json.dumps(get_type(init_arg))
                }
            )

        for init_arg in lib.kwargs.all():
            if init_arg.name not in init_args_names:
                init_arg.delete()

    lib.import_keywords(libdoc_dict, typedocs)
    lib.init_doc = lib.replace_links(str(lib.init_doc), typedocs)
    lib.documentation = lib.replace_links(lib.documentation, typedocs)
    lib.save()

    return lib
