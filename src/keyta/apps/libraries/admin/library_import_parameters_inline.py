from django.contrib import admin
from django.db.models import QuerySet
from django.utils.translation import gettext as _

from keyta.apps.libraries.models import LibraryImportParameter
from keyta.forms import OptionalArgumentFormSet


class LibraryImportParametersInline(admin.TabularInline):
    model = LibraryImportParameter
    fields = ['name', 'value']
    formset = OptionalArgumentFormSet
    readonly_fields = ['name']
    extra = 0
    max_num = 0
    verbose_name_plural = _('Einstellungen')
    can_delete = False

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)
        return queryset.filter(user=request.user)

    def name(self, obj: LibraryImportParameter):
        return obj.name
