import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from keyta.widgets import KeywordCallSelect

from ..models.keywordcall_parameters import JSONValue
from ..models import (
    KeywordCall,
    KeywordCallParameterSource,
    KeywordCallParameter
)


def show_value(json_value: JSONValue) -> tuple:
    if json_value.user_input:
        return json_value.jsonify(), json_value.user_input

    return None, _('Kein Wert')


class DynamicChoiceField(forms.CharField):
    def to_python(self, value: str):
        if not value:
            raise ValidationError(_('Das Feld darf nicht leer sein'))

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
        system_ids = list(
            kw_call.from_keyword.systems.values_list('pk', flat=True)
        )
        window_ids = list(
            kw_call.from_keyword.windows.values_list('pk', flat=True)
        )

        return (
            self.get_keyword_parameters(kw_call) + 
            self.get_prev_return_values() + 
            self.get_window_variables(window_ids, system_ids)
        )

    def get_keyword_parameters(self, kw_call: KeywordCall):
        return [[
            _('Parameters'),
            [
                (source.get_value().jsonify(), str(source))
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
                (source.get_value().jsonify(), str(source))
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
                (source.get_value().jsonify(), str(source))
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
        system_ids: list[int]
    ):
        return [[
            _('Referenzwerte'),
            [
                (source.get_value().jsonify(), str(source))
                for source in
                KeywordCallParameterSource.objects
                .filter(variable_value__variable__windows__in=window_ids)
                .filter(variable_value__variable__systems__in=system_ids)
                .distinct()
            ]
        ]]
