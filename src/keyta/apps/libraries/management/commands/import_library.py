from typing import Any

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from apps.rf_import.import_library import import_library


class Command(BaseCommand):
    help = """
    Imports the specified Robot Framework library
    """

    def add_arguments(self, parser):
        parser.add_argument("library", nargs=1, type=str)

    def handle(self, *args: Any, **options: Any) -> None:
        library = options["library"][0]
        import_library(library)
        print(_('The library {library} was successfully imported.').format(library=library))
