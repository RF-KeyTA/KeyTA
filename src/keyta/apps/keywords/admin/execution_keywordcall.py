from django.contrib import admin
from django.http import HttpRequest

from keyta.apps.variables.models import Variable

from ..forms import KeywordCallParameterFormsetWithErrors
from ..forms.keywordcall_parameter_formset import get_variables_choices
from ..models import ExecutionKeywordCall, KeywordCall
from .keywordcall import KeywordCallAdmin
from .keywordcall_parameters_inline import KeywordCallParametersInline


def get_window_variables(window):
    variables = Variable.objects.filter(windows__in=[window])
    return get_variables_choices(variables)


class ExecutionKeywordCallParameterFormset(KeywordCallParameterFormsetWithErrors):
    def get_ref_choices(self, kw_call: KeywordCall):
        exec_keyword = kw_call.to_keyword

        if exec_keyword.is_sequence:
            return get_window_variables(exec_keyword.windows.first())

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
        return self.changeform_view(request, object_id, form_url, extra_context or {'show_delete': False})

    def get_inlines(self, request, obj):
        return [ExecutionKeywordCallParametersInline]
