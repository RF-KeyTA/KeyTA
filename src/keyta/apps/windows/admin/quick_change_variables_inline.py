from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.apps.variables.models import VariableWindowRelation
from keyta.forms import form_with_select

from ..forms import VariablesFormset


class QuickChangeVariables(BaseTabularInline):
    model = VariableWindowRelation
    form = form_with_select(
        VariableWindowRelation,
        'variable',
        '',
        labels={
            'variable': _('Referenzwert')
        }
    )
    formset = VariablesFormset
    readonly_fields = []

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(variable__table__isnull=False)

    def has_change_permission(self, request, obj=None):
        return True
