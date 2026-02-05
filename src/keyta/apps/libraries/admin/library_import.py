from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_admin import BaseAdmin
from keyta.widgets import open_link_in_modal

from ..models import LibraryImport, LibraryInitDocumentation
from .library_import_parameters_inline import LibraryImportParametersInline


@admin.register(LibraryImport)
class LibraryImportAdmin(BaseAdmin):
    change_form_template = 'library_change_form.html'
    form = forms.modelform_factory(
        LibraryImport,
        fields=['keyword'],
        labels = {
            'keyword': _('Aktion')
        }
    )

    def get_fields(self, request, obj=None):
        return self.get_readonly_fields(request, obj)

    def get_inlines(self, request, obj):
        library_import: LibraryImport = obj
        
        if library_import.execution:
            return [LibraryImportParametersInline]
        
        return []

    def get_protected_objects(self, obj: LibraryImport):
        if keyword := obj.keyword:
            return keyword.calls.filter(to_keyword__library_id=obj.library.pk)

        return []

    def get_readonly_fields(self, request, obj=None):
        library_import: LibraryImport = obj

        if library_import.execution:
            return ['library_init_doc']
        
        return ['keyword']

    def get_related_objects(self, obj: LibraryImport):
        return self.get_protected_objects(obj)

    @admin.display(description=_('Dokumentation'))
    def library_init_doc(self, lib_import: LibraryImport):
        init_doc = LibraryInitDocumentation.objects.get(pk=lib_import.library.pk)

        return open_link_in_modal(
            init_doc.get_admin_url(),
            f'{init_doc} ' + _('Einstellungen')
        )
