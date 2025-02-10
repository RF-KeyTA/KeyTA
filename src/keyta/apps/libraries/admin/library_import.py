from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.admin.base_admin import BaseAdmin
from keyta.widgets import open_link_in_modal

from ..models import LibraryImport
from .library_import_parameters_inline import LibraryImportParametersInline


@admin.register(LibraryImport)
class LibraryImportAdmin(BaseAdmin):
    fields = ['library_init_doc']
    readonly_fields = ['library_init_doc']
    inlines = [
        LibraryImportParametersInline
    ]

    @admin.display(description=_('Dokumentation'))
    def library_init_doc(self, obj: LibraryImport):
        return open_link_in_modal(
            obj.library.get_admin_url('libraryinitdocumentation'),
            obj.library.name + _(' Einstellungen')
        )
