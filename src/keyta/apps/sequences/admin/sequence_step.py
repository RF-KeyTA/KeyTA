from django.conf import settings
from django.contrib import admin
from django.http.response import JsonResponse

from keyta.apps.keywords.admin import ConditionsInline, KeywordCallAdmin, KeywordCallParametersInline, ReadOnlyReturnValuesInline
from keyta.apps.keywords.forms.keywordcall_parameter_formset import (
    KeywordCallParameterFormsetWithErrors, get_prev_return_values, get_keyword_parameters
)

from ..models import SequenceStep


def get_choices_groups(sequence_step: SequenceStep):
    choices = []

    if parameters := get_keyword_parameters(sequence_step):
        choices.append({
            'icon': settings.FA_ICONS.arg_kw_param,
            'group': parameters
        })

    if prev_return_values := get_prev_return_values(sequence_step):
        choices.append({
            'icon': settings.FA_ICONS.arg_return_value,
            'group': prev_return_values
        })

    return choices


class SequenceStepParameterFormset(KeywordCallParameterFormsetWithErrors):
    def get_choices_groups(self, sequence_step: SequenceStep):
        return get_choices_groups(sequence_step)


class SequenceStepParametersInline(KeywordCallParametersInline):
    formset = SequenceStepParameterFormset


@admin.register(SequenceStep)
class SequenceStepAdmin(KeywordCallAdmin):
    def change_view(self, request, object_id, form_url="", extra_context=None):
        if _type := request.GET.get('_type') == 'query':
            sequence_step = SequenceStep.objects.get(pk=object_id)

            return JsonResponse({
                'results': self.get_select2_choices(request, sequence_step, get_choices_groups(sequence_step))
            })

        return self.changeform_view(request, object_id, form_url, extra_context or {'show_delete': False})

    def get_inlines(self, request, obj):
        sequence_step: SequenceStep = obj
        inlines = []

        if sequence_step.parameters.exists():
            inlines.append(SequenceStepParametersInline)
            inlines.extend(self.inlines)

        if sequence_step.return_values.exists():
            inlines.append(ReadOnlyReturnValuesInline)

        if sequence_step.from_keyword.parameters.exists() or sequence_step.get_previous_return_values().exists():
            for condition in sequence_step.conditions.all():
                condition.update_expected_value()

            return inlines + [ConditionsInline]

        return inlines
