from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import BaseTabularInline

from ..forms import LibraryParameterFormSet
from ..models import LibraryImportParameter


class LibraryImportParametersInline(BaseTabularInline):
    model = LibraryImportParameter
    fields = ['name', 'value']
    formset = LibraryParameterFormSet
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
