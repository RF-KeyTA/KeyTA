from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponse

from keyta.admin.base_admin import BaseAdmin
from keyta.apps.actions.admin.library_keyword_call_vararg_parameters_inline import VarargParametersInline
from keyta.apps.actions.models import ActionStep
from keyta.apps.executions.models import Setup, Teardown
from keyta.apps.sequences.models import SequenceStep
from keyta.apps.testcases.models import TestStep
from keyta.widgets import url_query_parameters

from ..models import (
    ExecutionKeywordCall,
    KeywordCall,
    KeywordParameterType
)
from ..models.keywordcall import KeywordCallType, TestSetupTeardown

from .field_parameters import repr_param
from .keywordcall_parameters_inline import KeywordCallParametersInline
from .keywordcall_return_value_inline import KeywordCallReturnValueInline, ReadOnlyReturnValuesInline


class UpdateIconHtmx:
    def update_icon(self, request, kw_call: KeywordCall):
        if request.GET.get('user') or kw_call.testcase:
            icon = kw_call.get_icon(request.user)
        else:
            icon = kw_call.get_icon()

        icon.attrs['style'] |= {'margin-left': '5px'}

        return HttpResponse(str(icon))


@admin.register(KeywordCall)
class KeywordCallAdmin(UpdateIconHtmx, BaseAdmin):
    parameters_inline = KeywordCallParametersInline
    change_form_template = 'keywordcall_change_form.html'

    def change_view(self, request, object_id, form_url="", extra_context=None):
        kw_call = KeywordCall.objects.get(pk=object_id)

        if request.GET.get('update-icon'):
            return self.update_icon(request, kw_call)

        kw_call.update_parameter_values()

        if param_position := request.GET.get('update-param'):
            if param := kw_call.get_parameter(int(param_position)):
                return HttpResponse(repr_param(param))

            return HttpResponse('')

        if kw_call.execution:
            if kw_call.type == KeywordCallType.KEYWORD_EXECUTION:
                execution_kwcall = ExecutionKeywordCall.objects.get(id=kw_call.pk)
                return HttpResponseRedirect(execution_kwcall.get_admin_url() + '?' + url_query_parameters(request.GET))

            if kw_call.type == TestSetupTeardown.TEST_SETUP:
                test_setup = Setup.objects.get(id=kw_call.pk)
                return HttpResponseRedirect(test_setup.get_admin_url() + '?' + url_query_parameters(request.GET))

            if kw_call.type == TestSetupTeardown.TEST_TEARDOWN:
                test_teardown = Teardown.objects.get(id=kw_call.pk)
                return HttpResponseRedirect(test_teardown.get_admin_url() + '?' + url_query_parameters(request.GET))

        if kw_call.from_keyword:
            if kw_call.from_keyword.is_action:
                library_kw_call = ActionStep.objects.get(id=kw_call.pk)
                # Do not forward the URL params of the current request. It breaks the conditions inline.
                return HttpResponseRedirect(library_kw_call.get_admin_url())

            if kw_call.from_keyword.is_sequence:
                sequence_step = SequenceStep.objects.get(pk=kw_call.pk)
                # Do not forward the URL params of the current request. It breaks the conditions inline.
                return HttpResponseRedirect(sequence_step.get_admin_url())

        if kw_call.testcase:
            test_step = TestStep.objects.get(pk=kw_call.pk)
            return HttpResponseRedirect(test_step.get_admin_url()  + '?' + url_query_parameters(request.GET))

        return super().change_view(request, object_id, form_url, extra_context)

    def get_fields(self, request, obj=None):
        return []

    def get_inlines(self, request, obj):
        kw_call: KeywordCall = obj

        inlines = []

        if kw_call.parameters.exclude(parameter__type=KeywordParameterType.VARARG).exists():
            inlines.append(self.parameters_inline)

        if vararg := kw_call.to_keyword.parameters.filter(type=KeywordParameterType.VARARG).first():
            inlines.append(VarargParametersInline)

        if kw_call.return_values.exists() and (kw_call.to_keyword.is_action or kw_call.to_keyword.is_sequence):
            inlines.append(ReadOnlyReturnValuesInline)

        if kw_call.to_keyword.resource or kw_call.to_keyword.library:
            inlines.append(KeywordCallReturnValueInline)

        return inlines

    def has_change_permission(self, request, obj=None):
        keywordcall: KeywordCall = obj

        if keywordcall and keywordcall.testcase:
            return self.can_change(request.user, 'testcase')

        return super().has_change_permission(request, obj)
