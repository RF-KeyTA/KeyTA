from django.utils.translation import gettext_lazy as _

from nonrelated_inlines.admin import NonrelatedInlineMixin

from keyta.admin.base_inline import BaseTabularInline
from keyta.apps.variables.models import VariableWindowRelation
from keyta.forms import form_with_select

from ..forms import VariablesFormset
from ..models import TestStep


class QuickChangeVariables(NonrelatedInlineMixin, BaseTabularInline):
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

    def get_form_queryset(self, obj):
        test_step: TestStep = obj

        return (
            self.model.objects
            .filter(window__in=[test_step.window])
            .filter(variable__template='')
            .exclude(variable__table__isnull=False)
        )

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(variable__table__isnull=False)

    def has_change_permission(self, request, obj=None):
        return True

    def save_new_instance(self, parent, instance):
        pass
