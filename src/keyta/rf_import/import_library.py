from keyta.apps.libraries.models import Library, LibraryParameter

from .import_keywords import (
    get_default_value,
    section_importing,
    get_init_doc,
    get_libdoc_json
)


def import_library(library_name: str):
    lib_json = get_libdoc_json(library_name)

    lib: Library
    lib, created = Library.objects.update_or_create(
        name=lib_json["name"],
        defaults={
            'version': lib_json["version"],
            'init_doc': get_init_doc(lib_json),
            'documentation': lib_json["doc"] + section_importing(lib_json)
        }
    )

    if lib_json["inits"]:
        init_args = lib_json["inits"][0]["args"]
        init_args_names = set()

        for init_arg in init_args:
            name = init_arg["name"]

            if name == '_':
                continue

            init_args_names.add(name)
            default_value = get_default_value(
                init_arg["defaultValue"],
                init_arg["kind"]
            )

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

    lib.import_keywords(lib_json)

    return lib
