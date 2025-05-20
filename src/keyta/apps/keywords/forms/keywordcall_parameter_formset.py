import re
from collections import defaultdict

from django import forms
from django.db.models import QuerySet
from django.forms.utils import ErrorDict, ErrorList
from django.utils.translation import gettext_lazy as _

from keyta.widgets import KeywordCallParameterSelect

from ..models.keywordcall_parameters import JSONValue
from ..models import (
    KeywordCall,
    KeywordCallParameterSource,
    KeywordCallParameter
)


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


def show_value(json_value: JSONValue) -> tuple:
    if json_value.user_input:
        return json_value.jsonify(), json_value.user_input

    return None, _('Kein Wert')


class DynamicChoiceField(forms.CharField):
    def to_python(self, value: str):
        if value.startswith('{') and value.endswith('}'):
            return value

        return JSONValue(
            arg_name=None,
            kw_call_index=None,
            pk=None,
            user_input=re.sub(r"\s{2,}", " ", value)
        ).jsonify()


class KeywordCallParameterFormset(forms.BaseInlineFormSet):
    def __init__(
        self,
        data=None,
        files=None,
        instance=None,
        save_as_new=False,
        prefix=None,
        queryset=None,
        **kwargs,
    ):
        super().__init__(data, files, instance, save_as_new, prefix, queryset, **kwargs)
        self.choices = self.get_choices(instance)

    def add_fields(self, form, index):
        super().add_fields(form, index)

        # The index of an extra form is None
        if index is not None:
            kw_call_parameter: KeywordCallParameter = form.instance
            json_value = kw_call_parameter.json_value
            choices = (
                    [(None, '')] +
                    [[_('Eingabe'), [show_value(json_value)]]] +
                    self.choices
            )

            form.fields['value'] = DynamicChoiceField(
                widget=KeywordCallParameterSelect(
                    _('Wert auswählen oder eintragen'),
                    choices=choices,
                    attrs={
                        # Allow manual input
                        'data-tags': 'true',
                    }
                )
            )

            if not json_value.user_input and not json_value.pk:
                form._errors = ErrorDict()
                form._errors['value'] = ErrorList([
                    form.fields['value'].default_error_messages['required']
                ])

    def get_choices(self, kw_call: KeywordCall):
        return get_keyword_parameters(kw_call) + get_prev_return_values(kw_call)

    def is_valid(self):
        return True
