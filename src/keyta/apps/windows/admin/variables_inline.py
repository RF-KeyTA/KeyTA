from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import BaseTabularInline
from keyta.apps.variables.models import VariableQuickAdd, VariableWindowRelation
from keyta.forms import form_with_select
from keyta.widgets import quick_change_widget, BaseSelect

from ..forms import QuickAddFormset


class VariablesFormset(QuickAddFormset):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        variable_field = form.fields['variable']

        # The index of extra forms is None
        if index is not None:
            variable_field.widget = quick_change_widget(variable_field.widget)
            variable_field.widget.widget = BaseSelect(
                '',
                attrs={'disabled': 'true'}
            )

    def quick_add_field(self) -> str:
        return 'variable'

    def quick_add_model(self):
        return VariableQuickAdd


class Variables(BaseTabularInline):
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
    readonly_fields = ['systems']

    @admin.display(description=_('Systeme'))
    def systems(self, obj):
        return ', '.join(obj.variable.systems.values_list('name', flat=True))

    def has_change_permission(self, request, obj=None):
        return False
