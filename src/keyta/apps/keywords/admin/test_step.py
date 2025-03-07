from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.widgets import open_link_in_modal

from apps.variables.models import VariableDocumentation

from ..forms import KeywordCallParameterFormset
from ..forms.keywordcall_parameter_formset import get_prev_return_values
from ..models import TestStep, KeywordCall, KeywordCallParameterSource
from .keywordcall import (
    KeywordCallParametersInline, 
    KeywordCallAdmin, 
    KeywordDocField, 
    ReturnValueField
)


def get_schema_fields(schema_pk, variable_name):
    sources = (
        KeywordCallParameterSource.objects
        .filter(variable_schema_field__schema_id=schema_pk)
    )

    return [[
        variable_name,
        [
            (source.get_value().jsonify(), str(source))
            for source in sources
        ]
    ]]


def get_variable_values(variable_pk, variable_name):
    sources = (
        KeywordCallParameterSource.objects
        .filter(variable_value__variable_id=variable_pk)
    )

    return [[
        variable_name,
        [
            (source.get_value().jsonify(), str(source))
            for source in sources
        ]
    ]]


class TestStepParameterFormset(KeywordCallParameterFormset):
    def get_choices(self, kw_call: KeywordCall):
        choices = get_prev_return_values(kw_call)

        if variable := kw_call.variable:
            if variable.is_list():
                choices += get_schema_fields(variable.schema.pk, variable.name)
            else:
                choices += get_variable_values(variable.pk, variable.name)

        return choices


class TestStepParametersInline(KeywordCallParametersInline):
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
    ReturnValueField,
    VariableDocField,
    KeywordDocField,
    KeywordCallAdmin
):
    parameters_inline = TestStepParametersInline
