from django.contrib import admin

from keyta.apps.variables.models import Variable, VariableValue
from keyta.apps.keywords.forms import KeywordCallParameterFormsetWithErrors
from keyta.apps.keywords.forms.keywordcall_parameter_formset import get_prev_return_values, get_variables_choices
from keyta.apps.keywords.models import KeywordCall, KeywordCallParameterSource
from keyta.apps.keywords.admin.keywordcall import (
    KeywordCallAdmin,
    KeywordCallParametersInline
)

from ..models import TestStep


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
    variable_values = VariableValue.objects.filter(
        variable__windows__in=[kw_call.window],
        variable__systems__in=kw_call.testcase.systems.all()
    )
    sources = (
        KeywordCallParameterSource.objects
        .filter(variable_value__in=variable_values)
        .exclude(variable_value__variable=exclude_variable)
    )

    return get_variables_choices(sources)


class TestStepParameterFormset(KeywordCallParameterFormsetWithErrors):
    def get_ref_choices(self, kw_call: KeywordCall):
        choices = get_prev_return_values(kw_call)

        if variable := kw_call.variable:
            return choices + get_variable_values(variable) + get_window_variables(kw_call, exclude_variable=variable)

        return choices + get_window_variables(kw_call)


class TestStepParametersInline(KeywordCallParametersInline):
    fields = ['name', 'value']
    formset = TestStepParameterFormset


@admin.register(TestStep)
class TestStepAdmin(
    KeywordCallAdmin
):
    parameters_inline = TestStepParametersInline

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return self.changeform_view(request, object_id, form_url, extra_context or {'show_delete': False})
