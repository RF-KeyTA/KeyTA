from typing import Any

from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

from keyta.rf_import.import_library import import_library
from keyta.rf_import.import_keywords import get_libdoc_dict


class Command(BaseCommand):
    help = """
    Imports the specified Robot Framework library
    """

    def add_arguments(self, parser):
        parser.add_argument("library", nargs=1, type=str)

    def handle(self, *args: Any, **options: Any) -> None:
        library = options["library"][0]
        libdoc_dict = get_libdoc_dict(library)
        import_library(libdoc_dict)
        print(_('Die Bibliothek "{library}" wurde erfolgreich importiert.').format(library=library))
