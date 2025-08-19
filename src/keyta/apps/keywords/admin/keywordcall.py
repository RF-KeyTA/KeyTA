from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_admin import BaseAdmin
from keyta.admin.base_inline import TabularInlineWithDelete
from keyta.apps.keywords.models import KeywordDocumentation
from keyta.apps.sequences.models import SequenceStep
from keyta.widgets import open_link_in_modal

from ..forms.library_keywordcall_vararg_formset import LibraryKeywordCallVarargFormset
from ..models import (
    ExecutionKeywordCall,
    KeywordCall,
    KeywordCallParameter,
    KeywordCallReturnValue,
    KeywordParameterType,
    LibraryKeywordCall,
    TestStep
)
from .keywordcall_parameters_inline import KeywordCallParametersInline
from .keywordcall_return_value_inline import KeywordCallReturnValueInline


class ReadOnlyReturnValuesInline(KeywordCallReturnValueInline):
    fields = ['return_value_name']
    readonly_fields = ['return_value_name']
    max_num = 0

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description=_('Name'))
    def return_value_name(self, return_value: KeywordCallReturnValue):
        return str(return_value)


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


class VarargForm(forms.ModelForm):
    def save(self, commit=True):
        kw_call_parameter: KeywordCallParameter = self.instance
        kw_call = kw_call_parameter.keyword_call
        vararg = kw_call.to_keyword.parameters.filter(type=KeywordParameterType.VARARG).first()
        kw_call_parameter.parameter = vararg

        return super().save(commit)


class VarargParametersInline(TabularInlineWithDelete):
    model = KeywordCallParameter
    fields = ['value']
    form = VarargForm
    formset = LibraryKeywordCallVarargFormset
    extra = 0

    def get_queryset(self, request):
        return super().get_queryset(request).filter(parameter__type=KeywordParameterType.VARARG)


@admin.register(KeywordCall)
class KeywordCallAdmin(BaseAdmin):
    parameters_inline = KeywordCallParametersInline
    change_form_template = 'keywordcall_change_form.html'

    def change_view(self, request, object_id, form_url="", extra_context=None):
        kw_call = KeywordCall.objects.get(pk=object_id)
        kw_call.update_parameter_values()

        if kw_call.execution:
            execution_kwcall = ExecutionKeywordCall.objects.get(id=kw_call.pk)
            return HttpResponseRedirect(execution_kwcall.get_admin_url())

        if kw_call.from_keyword:
            if kw_call.from_keyword.is_action:
                library_kw_call = LibraryKeywordCall.objects.get(id=kw_call.pk)
                return HttpResponseRedirect(library_kw_call.get_admin_url())

            if kw_call.from_keyword.is_sequence:
                sequence_step = SequenceStep.objects.get(pk=kw_call.pk)
                return HttpResponseRedirect(sequence_step.get_admin_url())

        if kw_call.testcase:
            test_step = TestStep.objects.get(pk=kw_call.pk)
            return HttpResponseRedirect(test_step.get_admin_url())

        return super().change_view(request, object_id, form_url, extra_context)

    def get_fields(self, request, obj=None):
        return []

    def get_inline_instances(self, request, obj=None):
        kw_call: KeywordCall = obj
        inline_instances = super().get_inline_instances(request, obj)

        for inline in inline_instances:
            if isinstance(inline, VarargParametersInline):
                vararg = kw_call.to_keyword.parameters.filter(type=KeywordParameterType.VARARG).first()
                inline.verbose_name_plural = vararg.name

        return inline_instances

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
