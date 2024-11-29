from importlib import import_module
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps.common.admin import BaseAdmin
from apps.common.forms import OptionalArgumentFormSet
from apps.common.widgets import link
from apps.rf_import.import_library import import_library
from ..forms import LibraryForm
from ..models import (
    Library,
    LibraryParameter,
    LibraryKeyword,
    LibraryInitDocumentation
)


class Keywords(admin.TabularInline):
    model = LibraryKeyword
    fields = ['name', 'short_doc']
    readonly_fields = ['name', 'short_doc']
    extra = 0
    can_delete = False
    show_change_link = True
    verbose_name_plural = 'Schlüsselwörter'

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class LibraryParameterFormSet(OptionalArgumentFormSet):
    value_field = 'default_value'


class InitArguments(admin.TabularInline):
    model = LibraryParameter
    fields = ['name', 'default_value', 'reset']
    readonly_fields = ['name', 'reset']
    formset = LibraryParameterFormSet
    extra = 0
    max_num = 0
    can_delete = False

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)
        return queryset.prefetch_related('library')

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description='zurücksetzen')
    def reset(self, obj: LibraryParameter):
        ref = '&ref=' + obj.library.get_admin_url() + obj.get_tab_url()
        url = obj.get_admin_url() + '?reset' + ref

        return link(url, '↩')


@admin.register(Library)
class LibraryAdmin(BaseAdmin):
    list_display = ['name', 'version', 'update']
    ordering = ['name']
    inlines = [Keywords]
    form = LibraryForm

    def get_changelist(self, request: HttpRequest, **kwargs):
        if 'update' in request.GET:
            library = Library.objects.get(id=int(request.GET['lib_id']))
            import_library(library.name)
            messages.info(request, f'Die Bibliothek "{library.name}" wurde erfolgreich aktualisiert')

        return super().get_changelist(request, **kwargs)


    def dokumentation(self, obj):
        return mark_safe(obj.documentation)

    def get_inlines(self, request, obj):
        library: Library = obj
        inlines = [Keywords]

        if library and library.has_parameters:
            return [InitArguments] + inlines

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

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def save_form(self, request, form, change):
        library_name = form.cleaned_data.get('name', None)

        if library_name:
            library = import_library(library_name)
            super().save_form(request, form, change)
            return library
        else:
            return super().save_form(request, form, change)

    @admin.display(description='Aktualisierung')
    def update(self, obj):
        library: Library = obj

        if library.name in Library.ROBOT_LIBRARIES:
            version = import_module(f'robot.libraries.{library.name}').get_version()
        else:
            version = getattr(import_module(library.name), '__version__', None)

        if version and version != library.version:
            return link(
                reverse('admin:libraries_library_changelist') + f'?update&lib_id={library.id}',
                '🔄'
            )

@admin.register(LibraryInitDocumentation)
class LibraryInitDocumentationAdmin(BaseAdmin):
    fields = ['dokumentation']
    readonly_fields = ['dokumentation']

    # noinspection PyMethodMayBeStatic
    def dokumentation(self, obj: Library):
        return mark_safe(obj.init_doc)