from django.contrib import admin
from django.http import HttpRequest

from ..forms import KeywordCallParameterFormset
from ..models import ExecutionKeywordCall, KeywordCall

from .keywordcall import KeywordCallAdmin
from .keywordcall_parameters_inline import KeywordCallParametersInline


class ExecutionKeywordCallParameterFormset(KeywordCallParameterFormset):
    def get_choices(self, kw_call: KeywordCall):
        return []


class ExecutionKeywordCallParametersInline(KeywordCallParametersInline):
    fields = ['name', 'value']
    readonly_fields = ['name']
    formset = ExecutionKeywordCallParameterFormset
    verbose_name_plural = ''

    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).filter(user=request.user)


@admin.register(ExecutionKeywordCall)
class ExecutionKeywordCallAdmin(KeywordCallAdmin):
    def change_view(self, request, object_id, form_url="", extra_context=None):
        return self.changeform_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def get_inlines(self, request, obj):
        return [ExecutionKeywordCallParametersInline]
