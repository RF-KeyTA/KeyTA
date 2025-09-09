from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.apps.variables.models import VariableWindowRelation
from keyta.forms import form_with_select

from ..forms import QuickChangeVariablesFormset


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
    formset = QuickChangeVariablesFormset
    readonly_fields = []

    @admin.display(description=_('Systeme'))
    def systems(self, obj):
        return ', '.join(obj.variable.systems.values_list('name', flat=True))

    def get_queryset(self, request):
        return super().get_queryset(request).filter(variable__template='')

    def has_change_permission(self, request, obj=None):
        return False
