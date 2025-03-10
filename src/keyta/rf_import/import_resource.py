from pathlib import Path

from keyta.apps.resources.models import Resource

from .import_keywords import get_libdoc_json


def import_resource(resource_path: str):
    lib_json = get_libdoc_json(resource_path)

    resource, created = Resource.objects.update_or_create(
        name=lib_json["name"],
        defaults={
            'documentation': lib_json["doc"],
            'path': Path(resource_path).as_posix()
        }
    )

    resource.import_keywords(lib_json)

    return resource
