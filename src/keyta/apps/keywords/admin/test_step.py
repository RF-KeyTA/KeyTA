from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.apps.variables.models import Variable, VariableDocumentation
from keyta.widgets import open_link_in_modal

from ..forms import KeywordCallParameterFormset
from ..forms.keywordcall_parameter_formset import get_prev_return_values, get_variables_choices
from ..models import TestStep, KeywordCall, KeywordCallParameterSource
from .keywordcall import (
    KeywordCallParametersInline, 
    KeywordCallAdmin, 
)


def get_variable_values(variable: Variable):
    sources = (
        KeywordCallParameterSource.objects
        .filter(variable_value__variable_id=variable.pk)
    )

    return [[
        variable.name,
        [
            (source.get_value().jsonify(), str(source))
            for source in sources
        ]
    ]]


def get_window_variables(kw_call: KeywordCall, exclude_variable: Variable=None):
    variable_values = kw_call.window.variables.values_list('values', flat=True)
    sources = (
        KeywordCallParameterSource.objects
        .filter(variable_value__in=variable_values)
        .exclude(variable_value__variable=exclude_variable)
    )

    return get_variables_choices(sources)


class TestStepParameterFormset(KeywordCallParameterFormset):
    def get_ref_choices(self, kw_call: KeywordCall):
        choices = get_prev_return_values(kw_call)

        if variable := kw_call.variable:
            return choices + get_variable_values(variable) + get_window_variables(kw_call, exclude_variable=variable)

        return choices + get_window_variables(kw_call)


class TestStepParametersInline(KeywordCallParametersInline):
    fields = ['name', 'value']
    formset = TestStepParameterFormset



class VariableDocField:
    @admin.display(description=_('Referenzwerte'))
    def variable_doc(self, test_step: TestStep):
        variable_doc = VariableDocumentation(test_step.variable.pk)

        return open_link_in_modal(
            variable_doc.get_admin_url(),
            test_step.variable.name
        )

    def get_fields(self, request, obj=None):
        test_step: TestStep = obj

        if test_step.variable:
            return super().get_fields(request, obj) + ['variable_doc']

        return super().get_fields(request, obj)

    def get_readonly_fields(self, request, obj=None):
        test_step: TestStep = obj

        if test_step.variable:
            return super().get_readonly_fields(request, obj) + ['variable_doc']

        return super().get_readonly_fields(request, obj)


@admin.register(TestStep)
class TestStepAdmin(
    KeywordCallAdmin
):
    parameters_inline = TestStepParametersInline

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return self.changeform_view(request, object_id, form_url, extra_context or {'show_delete': False})
