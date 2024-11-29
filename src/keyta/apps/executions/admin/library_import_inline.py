from django.contrib import admin
from django.db.models import QuerySet

from apps.common.forms import OptionalArgumentFormSet
from apps.common.widgets import open_link_in_modal
from apps.libraries.models import LibraryImportParameter
from ..models import ExecutionLibraryImport


class LibraryImportsInline(admin.TabularInline):
    model = ExecutionLibraryImport
    fields = ['library', 'args']
    readonly_fields = ['library', 'args']
    extra = 1
    max_num = 1
    can_delete = False
    verbose_name_plural = 'Bibliotheken'

    @admin.display(description='Einstellungen')
    def args(self, obj: ExecutionLibraryImport):
        if obj.kwargs.exists():
            return open_link_in_modal(
                obj.get_admin_url(),
                '<i class=" fa-solid fa-list" style="font-size: 36px"></i>'
            )

        return ''


class LibraryImportParameters(admin.TabularInline):
    model = LibraryImportParameter
    fields = ['name', 'value']
    formset = OptionalArgumentFormSet
    readonly_fields = ['name']
    extra = 0
    max_num = 0
    verbose_name_plural = 'Einstellungen'
    can_delete = False

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)
        return queryset.filter(user=request.user)

    def name(self, obj: LibraryImportParameter):
        return obj.name


@admin.register(ExecutionLibraryImport)
class ExecutionLibraryImportAdmin(admin.ModelAdmin):
    fields = ['library_init_doc']
    readonly_fields = ['library_init_doc']
    inlines = [LibraryImportParameters]

    @admin.display(description='Dokumentation')
    def library_init_doc(self, obj: ExecutionLibraryImport):
        return open_link_in_modal(
            obj.library.get_admin_url('libraryinitdocumentation'),
            obj.library.name + ' Einstellungen'
        )
