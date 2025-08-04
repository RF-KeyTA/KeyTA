from pathlib import Path

from keyta.apps.resources.models import Resource

from .import_keywords import get_libdoc_dict


def import_resource(resource_path: str):
    libdoc_dict = get_libdoc_dict(resource_path)

    resource, created = Resource.objects.update_or_create(
        name=libdoc_dict["name"],
        defaults={
            'documentation': libdoc_dict["doc"],
            'path': Path(resource_path).as_posix()
        }
    )

    resource.import_keywords(libdoc_dict)

    return resource
