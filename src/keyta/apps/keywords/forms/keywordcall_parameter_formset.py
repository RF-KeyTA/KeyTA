import re
from typing import Callable

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from keyta.apps.keywords.models import (
    KeywordCall,
    KeywordCallParameterSource,
    KeywordCallParameter
)
from keyta.select_value import SelectValue
from keyta.widgets import KeywordCallSelect


def jsonify_value(value):
    return SelectValue(
        arg_name=None,
        kw_call_index=None,
        pk=None,
        user_input=re.sub(r"\s{2,}", " ", value)
    ).jsonify()


def show_value(json_str: str) -> tuple:
    select_value = SelectValue.from_json(json_str)

    if select_value.user_input:
        return json_str, select_value.user_input
    else:
        return None, 'Kein Wert'


class DynamicChoiceField(forms.CharField):
    def to_python(self, value: str):
        if not value:
            raise ValidationError(_('Das Feld darf nicht leer sein'))

        if value.startswith('{') and value.endswith('}'):
            return value

        return jsonify_value(value)


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

        if index is not None:
            kw_call_parameter: KeywordCallParameter = form.instance
            current_value = kw_call_parameter.value
            value, displayed_value = show_value(current_value)

            if value and displayed_value in {'True', 'False'}:
                choices = [
                    (jsonify_value('True'), 'True'),
                    (jsonify_value('False'), 'False'),
                ]
            else:
                choices = (
                        [(None, '')] +
                        [[_('Eingabe'), [show_value(current_value)]]] +
                        self.choices
                )

            form.fields['value'] = DynamicChoiceField(
                widget=KeywordCallSelect(
                    choices=choices,
                    attrs={
                        # Allow manual input
                        'data-tags': 'true',
                        'data-width': '60%',
                        'data-placeholder': _('Wert auswählen oder eintragen')
                    }
                )
            )

            if kw_call_parameter.parameter.is_list:
                form.fields['value'].help_text = _('Wert 1, Wert 2, ...')

    def get_choices(self, kw_call: KeywordCall):
        return self.get_keyword_parameters(kw_call) + self.get_prev_return_values()

    def get_keyword_parameters(self, kw_call: KeywordCall):
        return [[
            _('Parameters'),
            [
                (source.jsonify(), str(source))
                for source in KeywordCallParameterSource.objects
                .filter(kw_param__keyword=kw_call.from_keyword)
            ]
        ]]

    def get_global_variables(
        self,
        system_ids: list[int]
    ):

        return [[
            _('Globale Referenzwerte'),
            [
                (source.jsonify(), str(source))
                for source in
                KeywordCallParameterSource.objects
                .filter(variable_value__variable__systems__in=system_ids)
                .filter(variable_value__variable__windows__isnull=True)
            ]
        ]]

    def get_prev_return_values(self):
        kw_call: KeywordCall = self.instance

        return [[
            _('Vorherige Rückgabewerte'),
            [
                (source.jsonify(), str(source))
                for source in
                KeywordCallParameterSource.objects
                .filter(
                    kw_call_ret_val__in=kw_call.get_previous_return_values()
                )
            ]
        ]]

    def get_window_variables(
        self,
        window_ids: list[int],
        system_ids: list[int],
        show: Callable[[KeywordCallParameterSource], str]
    ):
        return [[
            _('Referenzwerte'),
            [
                (source.jsonify(), show(source))
                for source in
                KeywordCallParameterSource.objects
                .filter(variable_value__variable__windows__in=window_ids)
                .filter(variable_value__variable__systems__in=system_ids)
                .distinct()
            ]
        ]]
