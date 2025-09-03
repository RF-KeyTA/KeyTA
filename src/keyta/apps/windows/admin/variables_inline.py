from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.apps.variables.models import VariableWindowRelation

from ..forms import VariablesFormset


class Variables(BaseTabularInline):
    model = VariableWindowRelation
    form = forms.modelform_factory(
        VariableWindowRelation,
        fields=['variable'],
        labels={
            'variable': _('Referenzwert')
        }
    )
    formset = VariablesFormset
    readonly_fields = ['systems']

    @admin.display(description=_('Systeme'))
    def systems(self, obj):
        return ', '.join(obj.variable.systems.values_list('name', flat=True))

    def has_change_permission(self, request, obj=None):
        return False
