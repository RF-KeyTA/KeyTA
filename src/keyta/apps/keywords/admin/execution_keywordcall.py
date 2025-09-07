from django.contrib import admin
from django.http import HttpRequest

from keyta.apps.variables.models import VariableValue

from ..forms import KeywordCallParameterFormset
from ..forms.keywordcall_parameter_formset import get_variables_choices
from ..models import ExecutionKeywordCall, KeywordCall, KeywordCallParameterSource
from .keywordcall import KeywordCallAdmin
from .keywordcall_parameters_inline import KeywordCallParametersInline


def get_window_variables(window):
    variable_values = VariableValue.objects.filter(
        variable__windows__in=[window],
    )
    sources = (
        KeywordCallParameterSource.objects
        .filter(variable_value__in=variable_values)
    )

    return get_variables_choices(sources)


class ExecutionKeywordCallParameterFormset(KeywordCallParameterFormset):
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
