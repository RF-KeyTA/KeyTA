from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.widgets import open_link_in_modal

from ..models import LibraryImport


class LibraryImportInline(admin.TabularInline):
    model = LibraryImport
    fields = ['library', 'args']
    readonly_fields = ['library', 'args']
    extra = 1
    max_num = 1
    can_delete = False
    verbose_name_plural = _('Bibliotheken')

    @admin.display(description=_('Einstellungen'))
    def args(self, obj: LibraryImport):
        if obj.kwargs.exists():
            return open_link_in_modal(
                obj.get_admin_url(),
                '<i class=" fa-solid fa-list" style="font-size: 36px"></i>'
            )

        return ''
