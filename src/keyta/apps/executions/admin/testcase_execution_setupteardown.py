from django.contrib import admin
from django.utils.translation import gettext as _

from apps.executions.admin import SetupTeardownAdmin
from apps.executions.admin import SetupTeardownParametersInline
from apps.executions.models import TestCaseExecutionSetupTeardown
from apps.keywords.forms import KeywordCallParameterFormset
from apps.keywords.models import KeywordCall, KeywordCallParameterSource
from apps.keywords.models.keywordcall_parameters import jsonify


class TestCaseSetupTeardownParametersFormset(KeywordCallParameterFormset):
    def get_choices(self, obj):
        kw_call: KeywordCall = obj

        if kw_call:
            system_ids = kw_call.execution.testcase.systems.values_list('id')

            return [[
                _('Referenzwerte'),
                [
                    (jsonify(None, source.pk), str(source))
                    for source in
                    KeywordCallParameterSource.objects
                    .filter(variable_value__variable__systems__in=system_ids)
                    .filter(variable_value__variable__windows__isnull=True)
                ]
            ]]

        return []


class TestCaseSetupTeardownParameters(SetupTeardownParametersInline):
    formset = TestCaseSetupTeardownParametersFormset


@admin.register(TestCaseExecutionSetupTeardown)
class TestCaseExecutionSetupTeardownAdmin(SetupTeardownAdmin):
    def get_inlines(self, request, obj):
        return [
            TestCaseSetupTeardownParameters
        ]
