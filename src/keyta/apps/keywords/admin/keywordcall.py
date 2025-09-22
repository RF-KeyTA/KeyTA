from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_admin import BaseAdmin
from keyta.apps.keywords.models import KeywordDocumentation
from keyta.apps.sequences.models import SequenceStep
from keyta.apps.testcases.models import TestStep
from keyta.widgets import open_link_in_modal, url_query_parameters

from ..models import (
    ExecutionKeywordCall,
    KeywordCall,
    KeywordParameterType,
    LibraryKeywordCall
)
from .keywordcall_parameters_inline import KeywordCallParametersInline
from .keywordcall_return_value_inline import KeywordCallReturnValueInline, ReadOnlyReturnValuesInline
from .library_keyword_call_vararg_parameters_inline import VarargParametersInline


class KeywordDocField:
    @admin.display(description=_('Dokumentation'))
    def to_keyword_doc(self, kw_call: KeywordCall):
        keyword_doc = KeywordDocumentation.objects.get(pk=kw_call.to_keyword.pk)

        return open_link_in_modal(
            keyword_doc.get_admin_url(),
            str(keyword_doc)
        )

    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj) + ['to_keyword_doc']

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj) + ['to_keyword_doc']


@admin.register(KeywordCall)
class KeywordCallAdmin(BaseAdmin):
    parameters_inline = KeywordCallParametersInline
    change_form_template = 'keywordcall_change_form.html'

    def change_view(self, request, object_id, form_url="", extra_context=None):
        kw_call = KeywordCall.objects.get(pk=object_id)

        if request.GET.get('update_icon'):
            if request.GET.get('user'):
                icon = kw_call.get_icon(request.user)
            else:
                icon = kw_call.get_icon()

            return HttpResponse(str(icon))

        kw_call.update_parameter_values()

        if param := request.GET.get('update_param'):
            return HttpResponse(kw_call.get_parameter_value(param) or '')

        if kw_call.execution:
            execution_kwcall = ExecutionKeywordCall.objects.get(id=kw_call.pk)
            return HttpResponseRedirect(execution_kwcall.get_admin_url() + '?' + url_query_parameters(request.GET))

        if kw_call.from_keyword:
            if kw_call.from_keyword.is_action:
                library_kw_call = LibraryKeywordCall.objects.get(id=kw_call.pk)
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
