from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import BaseTabularInline

from ..forms import LibraryParameterFormSet
from ..models import LibraryImportParameter


class LibraryImportParametersInline(BaseTabularInline):
    model = LibraryImportParameter
    fields = ['name', 'value']
    readonly_fields = ['name']
    formset = LibraryParameterFormSet
    extra = 0
    max_num = 0
    verbose_name_plural = _('Einstellungen')
    can_delete = False

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        queryset: QuerySet = super().get_queryset(request)
        return queryset.filter(user=request.user)

    def name(self, kwarg: LibraryImportParameter):
        return str(kwarg)
