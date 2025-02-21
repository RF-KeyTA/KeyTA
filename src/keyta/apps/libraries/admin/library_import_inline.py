from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.widgets import open_link_in_modal, Icon

from ..models import LibraryImport


class LibraryImportInline(BaseTabularInline):
    model = LibraryImport
    fields = ['library', 'args']
    readonly_fields = ['args']
    extra = 0
    max_num = 0
    can_delete = False
    verbose_name = _('Bibliothek')
    verbose_name_plural = _('Bibliotheken')

    @admin.display(description=_('Einstellungen'))
    def args(self, lib_import: LibraryImport):
        if lib_import.kwargs.exists():
            icon = Icon(settings.FA_ICONS.library_import_args)

            return open_link_in_modal(
                lib_import.get_admin_url(),
                str(icon)
            )

        return ''

    def has_change_permission(self, request, obj=None) -> bool:
        return False
