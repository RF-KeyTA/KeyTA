from django.contrib import admin

from keyta.apps.keywords.admin import KeywordCallAdmin
from keyta.apps.keywords.admin.field_keyword_documentation import KeywordDocField
from keyta.apps.keywords.admin.keywordcall_conditions_inline import ConditionsInline
from keyta.apps.keywords.models import KeywordCall

from ..models import ActionStep
from .library_keyword_call_parameters_inline import LibraryKeywordCallParametersInline


@admin.register(ActionStep)
class ActionStepAdmin(
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
