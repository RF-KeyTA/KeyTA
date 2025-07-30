from collections import defaultdict

from django.db.models import QuerySet
from django.forms.utils import ErrorDict, ErrorList
from django.utils.translation import gettext_lazy as _

from ..json_value import JSONValue
from ..models import (
    KeywordCall,
    KeywordCallParameterSource,
    KeywordCallParameter
)
from .user_input_formset import UserInputFormset


def get_global_variables(system_ids: list[int]):
    sources = (
        KeywordCallParameterSource.objects
        .filter(variable_value__variable__systems__in=system_ids)
        .filter(variable_value__variable__windows__isnull=True)
        .distinct()
    )

    return get_variables_choices(sources)


def get_keyword_parameters(kw_call: KeywordCall):
    if not kw_call.from_keyword or not kw_call.from_keyword.parameters.exists():
        return []

    return [[
        _('Parameters'),
        [
            (source.get_value().jsonify(), str(source))
            for source in KeywordCallParameterSource.objects
            .filter(kw_param__keyword=kw_call.from_keyword)
        ]
    ]]


def get_prev_return_values(kw_call: KeywordCall):
    prev_return_values = kw_call.get_previous_return_values()

    if not prev_return_values.exists():
        return []

    sources = KeywordCallParameterSource.objects.filter(
        kw_call_ret_val__in=prev_return_values
    )

    return [[
        _('Vorherige Rückgabewerte'),
        [
            (source.get_value().jsonify(), str(source))
            for source in sources
        ]
    ]]


def get_variables_choices(kw_call_param_sources: QuerySet):
    variable_names = [source.variable_value.variable.name for source in kw_call_param_sources]
    grouped_variable_values = defaultdict(list)

    for variable_name, source in zip(variable_names, kw_call_param_sources):
        grouped_variable_values[variable_name].append((source.get_value().jsonify(), str(source)))

    return [
        [
            variable,
            values
        ]
        for variable, values in grouped_variable_values.items()
    ]


class KeywordCallParameterFormset(UserInputFormset):
    json_field_name = 'value'

    def form_errors(self, form):
        if json_field := getattr(form.instance, self.json_field_name):
            value = JSONValue.from_json(json_field)

            if not value.user_input and not value.pk:
                form._errors = ErrorDict()
                form._errors[self.json_field_name] = ErrorList([
                    form.fields[self.json_field_name].default_error_messages['required']
                ])

    def get_choices(self, kw_call: KeywordCall):
        return get_keyword_parameters(kw_call) + get_prev_return_values(kw_call)

    def get_json_value(self, form):
        kw_call_parameter: KeywordCallParameter = form.instance
        return kw_call_parameter.json_value

    # This is necessary in order to be able to save the formset
    # despite the errors that were added in form_errors
    def is_valid(self):
        return True
