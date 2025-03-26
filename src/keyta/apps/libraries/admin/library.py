import json
from importlib import import_module

from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from keyta.admin.base_admin import BaseAdmin
from keyta.admin.keywords_inline import Keywords
from keyta.rf_import.import_library import import_library
from keyta.widgets import link, Icon

from ..forms import LibraryForm
from ..models import (
    Library,
    LibraryInitDocumentation
)
from .library_parameters_inline import InitArguments


@admin.register(Library)
class LibraryAdmin(BaseAdmin):
    list_display = ['name', 'version', 'update']
    inlines = [Keywords]
    form = LibraryForm
    errors = set()

    def autocomplete_name(self, name: str, request: HttpRequest):
        return json.dumps([
            name
            for name in
            self.model.objects.values_list('name', flat=True)
            .filter(name__icontains=name)
        ])

    def get_changelist(self, request: HttpRequest, **kwargs):
        if 'update' in request.GET:
            library = Library.objects.get(id=int(request.GET['lib_id']))
            import_library(library.name)
            messages.info(
                request,
                _('Die Bibliothek "{library_name}" wurde erfolgreich aktualisiert').format(library_name=library.name)
            )

        for error in self.errors:
            messages.warning(request, error)

        return super().get_changelist(request, **kwargs)

    @admin.display(description=_('Dokumentation'))
    def dokumentation(self, library: Library):
        return mark_safe(library.documentation)

    def get_inlines(self, request, obj):
        library: Library = obj
        inlines = [Keywords]

        if library and library.has_parameters:
            return inlines + [InitArguments]

        if library:
            return inlines

        return []

    def get_fields(self, request, obj=None):
        library: Library = obj

        if not library:
            return ['name']

        return ['version', 'dokumentation']

    def get_readonly_fields(self, request, obj=None):
        library: Library = obj

        if not library:
            return []

        return ['name', 'version', 'dokumentation']

    def save_form(self, request, form, change):
        library_name = form.cleaned_data.get('name', None)

        if library_name:
            library = import_library(library_name)
            super().save_form(request, form, change)
            return library
        else:
            return super().save_form(request, form, change)

    @admin.display(description=_('Aktualisierung'))
    def update(self, library: Library):
        version = None

        if library.name in Library.ROBOT_LIBRARIES:
            version = import_module(f'robot.libraries.{library.name}').get_version()
        else:
            try:
                version = getattr(import_module(library.name), '__version__', None) 
            except ModuleNotFoundError as err:
                self.errors.add(_('Eine Bibliothek ist nicht vorhanden: {err}').format(err=err))

        if version and version != library.version:
            return link(
                reverse('admin:libraries_library_changelist') + f'?update&lib_id={library.id}',
                str(Icon(settings.FA_ICONS.library_update, {'font-size': '18px'}))
            )


@admin.register(LibraryInitDocumentation)
class LibraryInitDocumentationAdmin(BaseAdmin):
    fields = ['dokumentation']
    readonly_fields = ['dokumentation']

    def dokumentation(self, library: Library):
        return mark_safe(library.init_doc)

    def has_delete_permission(self, request, obj=None):
        return False
