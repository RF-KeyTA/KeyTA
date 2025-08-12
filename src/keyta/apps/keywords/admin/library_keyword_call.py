from django.contrib import admin

from keyta.admin.base_inline import TabularInlineWithDelete

from ..forms import KeywordCallParameterFormset, KeywordCallConditionFormset
from ..forms.keywordcall_parameter_formset import get_global_variables
from ..models import (
    KeywordCall,
    KeywordCallCondition,
    LibraryKeywordCall
)
from .keywordcall import KeywordCallAdmin, KeywordDocField
from .keywordcall_parameters_inline import KeywordCallParametersInline


class LibraryKeywordCallParameterFormset(KeywordCallParameterFormset):
    def get_ref_choices(self, kw_call: KeywordCall):
        if not kw_call.from_keyword.windows.count():
            system_ids = list(kw_call.from_keyword.systems.values_list('id', flat=True))
            return super().get_ref_choices(kw_call) + get_global_variables(system_ids)

        return super().get_ref_choices(kw_call)


class LibraryKeywordCallParametersInline(KeywordCallParametersInline):
    formset = LibraryKeywordCallParameterFormset


class ConditionsInline(TabularInlineWithDelete):
    model = KeywordCallCondition
    fields = ['value_ref', 'condition', 'expected_value']
    formset = KeywordCallConditionFormset


@admin.register(LibraryKeywordCall)
class LibraryKeywordCallAdmin(
    KeywordDocField,
    KeywordCallAdmin
):
    parameters_inline = LibraryKeywordCallParametersInline

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return self.changeform_view(request, object_id, form_url, extra_context or {'show_delete': False})

    def get_inlines(self, request, obj):
        inlines = super().get_inlines(request, obj)
        kw_call: KeywordCall = obj

        if kw_call.from_keyword.parameters.exists() or kw_call.get_previous_return_values().exists():
            for condition in kw_call.conditions.all():
                condition.update_expected_value()

            return inlines + [ConditionsInline]

        return inlines
