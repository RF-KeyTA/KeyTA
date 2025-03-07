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
    verbose_name_plural = ''

    formset = ExecutionKeywordCallParameterFormset

    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).filter(user=request.user)


@admin.register(ExecutionKeywordCall)
class ExecutionKeywordCallAdmin(KeywordCallAdmin):
    readonly_fields = []

    def change_view(self, request: HttpRequest, object_id, form_url="", extra_context=None):
        kw_call = ExecutionKeywordCall.objects.get(id=object_id)
        kw_call.update_parameters(request.user)

        return super().change_view(request, object_id, form_url, extra_context)

    def get_fields(self, request, obj=None):
        return []

    def get_inlines(self, request, obj):
        return [ExecutionKeywordCallParametersInline]
