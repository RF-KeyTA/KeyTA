from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.admin.field_delete_related_instance import DeleteRelatedField
from keyta.apps.variables.models import VariableWindowRelation
from keyta.forms import form_with_select

from ..forms import QuickChangeTemplateVariablesFormset


class QuickChangeTemplateVariables(
    DeleteRelatedField,
    BaseTabularInline
):
    model = VariableWindowRelation
    form = form_with_select(
        VariableWindowRelation,
        'variable',
        '',
        labels={
            'variable': _('Referenzwert')
        }
    )
    formset = QuickChangeTemplateVariablesFormset

    verbose_name = _('Dynamischer Wert')
    verbose_name_plural = _('Dynamische Werte')

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(variable__template='')

    def has_change_permission(self, request, obj=None):
        return True
