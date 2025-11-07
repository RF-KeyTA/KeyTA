from django.conf import settings
from django.contrib import admin
from django.http.response import JsonResponse

from keyta.apps.keywords.admin import KeywordCallAdmin, KeywordCallParametersInline, ReadOnlyReturnValuesInline
from keyta.apps.keywords.admin.field_keyword_documentation import KeywordDocField
from keyta.apps.keywords.admin.keywordcall_conditions_inline import ConditionsInline
from keyta.apps.keywords.forms.keywordcall_parameter_formset import (
    get_keyword_parameters,
    get_prev_return_values,
    KeywordCallParameterFormsetWithErrors
)
from keyta.apps.keywords.models import (
    KeywordParameterType
)

from ..models import ActionStep
from .library_keyword_call_parameters_inline import LibraryKeywordCallParametersInline
from .library_keyword_call_vararg_parameters_inline import VarargParametersInline


def get_choices_groups(action_step: ActionStep):
    choices = []

    if parameters := get_keyword_parameters(action_step):
        choices.append({
            'icon': settings.FA_ICONS.arg_kw_param,
            'group': parameters
        })

    if prev_return_values := get_prev_return_values(action_step):
        choices.append({
            'icon': settings.FA_ICONS.arg_return_value,
            'group': prev_return_values
        })

    return choices


class ActionStepParameterFormset(KeywordCallParameterFormsetWithErrors):
    def get_choices_groups(self, action_step: ActionStep):
        return get_choices_groups(action_step)


class ActionStepParametersInline(KeywordCallParametersInline):
    formset = ActionStepParameterFormset



@admin.register(ActionStep)
class ActionStepAdmin(
    KeywordDocField,
    KeywordCallAdmin
):
    parameters_inline = LibraryKeywordCallParametersInline

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if _type := request.GET.get('_type') == 'query':
            action_step = ActionStep.objects.get(pk=object_id)

            return JsonResponse({
                'results': self.get_select2_choices(request, action_step, get_choices_groups(action_step))
            })

        return self.changeform_view(request, object_id, form_url, extra_context or {'show_delete': False})

    def get_inline_instances(self, request, obj=None):
        action_step: ActionStep = obj
        inline_instances = super().get_inline_instances(request, obj)

        for inline in inline_instances:
            if isinstance(inline, VarargParametersInline):
                vararg = action_step.to_keyword.parameters.filter(type=KeywordParameterType.VARARG).first()
                inline.verbose_name_plural = vararg.name

        return inline_instances

    def get_inlines(self, request, obj):
        action_step: ActionStep = obj
        inlines = []

        if action_step.parameters.exists():
            inlines.append(ActionStepParametersInline)
            inlines.extend(self.inlines)

        if action_step.return_values.exists():
            inlines.append(ReadOnlyReturnValuesInline)

        if action_step.from_keyword.parameters.exists() or action_step.get_previous_return_values().exists():
            for condition in action_step.conditions.all():
                condition.update_expected_value()

            return inlines + [ConditionsInline]

        return inlines
