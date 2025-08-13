from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_admin import BaseAdmin
from keyta.widgets import open_link_in_modal

from ..models import LibraryImport
from .library_import_parameters_inline import LibraryImportParametersInline


@admin.register(LibraryImport)
class LibraryImportAdmin(BaseAdmin):
    change_form_template = 'library_change_form.html'

    def get_fields(self, request, obj=None):
        return self.get_readonly_fields(request, obj)

    def get_form(self, request, obj=None, change=False, **kwargs):
        return forms.modelform_factory(
            LibraryImport,
            fields=['keyword'],
            labels = {
                'keyword': _('Aktion')
            }
        )

    def get_inlines(self, request, obj):
        library_import: LibraryImport = obj
        
        if library_import.execution:
            return [LibraryImportParametersInline]
        
        return []

    def get_readonly_fields(self, request, obj=None):
        library_import: LibraryImport = obj

        if library_import.execution:
            return ['library_init_doc']
        
        return ['keyword']

    @admin.display(description=_('Dokumentation'))
    def library_init_doc(self, obj: LibraryImport):
        return open_link_in_modal(
            obj.library.get_admin_url(model='libraryinitdocumentation'),
            obj.library.name + _(' Einstellungen')
        )
