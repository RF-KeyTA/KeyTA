from django.contrib import admin

from keyta.apps.keywords.admin import KeywordCallAdmin
from keyta.apps.keywords.admin.field_keyword_documentation import KeywordDocField
from keyta.apps.keywords.admin.keywordcall_conditions_inline import ConditionsInline
from keyta.apps.keywords.models import (
    KeywordCall,
    KeywordParameterType
)

from ..models import ActionStep
from .library_keyword_call_parameters_inline import LibraryKeywordCallParametersInline
from .library_keyword_call_vararg_parameters_inline import VarargParametersInline


@admin.register(ActionStep)
class ActionStepAdmin(
    KeywordDocField,
    KeywordCallAdmin
):
    parameters_inline = LibraryKeywordCallParametersInline

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return self.changeform_view(request, object_id, form_url, extra_context or {'show_delete': False})

    def get_inline_instances(self, request, obj=None):
        kw_call: KeywordCall = obj
        inline_instances = super().get_inline_instances(request, obj)

        for inline in inline_instances:
            if isinstance(inline, VarargParametersInline):
                vararg = kw_call.to_keyword.parameters.filter(type=KeywordParameterType.VARARG).first()
                inline.verbose_name_plural = vararg.name

        return inline_instances

    def get_inlines(self, request, obj):
        inlines = super().get_inlines(request, obj)
        kw_call: KeywordCall = obj

        if kw_call.from_keyword.parameters.exists() or kw_call.get_previous_return_values().exists():
            for condition in kw_call.conditions.all():
                condition.update_expected_value()

            return inlines + [ConditionsInline]

        return inlines
