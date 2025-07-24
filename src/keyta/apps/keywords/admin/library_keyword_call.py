from django.contrib import admin

from keyta.admin.base_inline import TabularInlineWithDelete

from ..forms import KeywordCallParameterFormset
from ..forms.keywordcall_parameter_formset import get_global_variables
from ..models import LibraryKeywordCall, KeywordCall, KeywordCallCondition
from .keywordcall import KeywordCallAdmin, KeywordDocField
from .keywordcall_parameters_inline import KeywordCallParametersInline


class LibraryKeywordCallParameterFormset(KeywordCallParameterFormset):
    def get_choices(self, kw_call: KeywordCall):
        if not kw_call.from_keyword.windows.count():
            system_ids = list(kw_call.from_keyword.systems.values_list('id', flat=True))
            return super().get_choices(kw_call) + get_global_variables(system_ids)

        return super().get_choices(kw_call)


class LibraryKeywordCallParametersInline(KeywordCallParametersInline):
    formset = LibraryKeywordCallParameterFormset


class ConditionsInline(TabularInlineWithDelete):
    model = KeywordCallCondition


@admin.register(LibraryKeywordCall)
class LibraryKeywordCallAdmin(
    KeywordDocField,
    KeywordCallAdmin
):
    parameters_inline = LibraryKeywordCallParametersInline

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return self.changeform_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def get_inlines(self, request, obj):
        return super().get_inlines(request, obj) + [ConditionsInline]
