import json
from typing import Callable

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import get_select2_language
from django.core.exceptions import ValidationError

from apps.keywords.models import (
    KeywordCall,
    KeywordCallParameterSource,
    KeywordCallParameter
)
from apps.keywords.models.keywordcall_parameters import jsonify


def show_value(json_str: str) -> tuple:
    value_pk = json.loads(json_str)
    value = value_pk['value']

    if value:
        return json_str, value
    else:
        return None, 'Kein Wert'


class DynamicChoiceField(forms.CharField):
    def to_python(self, value: str):
        if not value:
            raise ValidationError('Das Feld darf nicht leer sein')

        if value.startswith('{') and value.endswith('}'):
            return value

        return jsonify(value, None)


class KeywordCallParameterFormset(forms.BaseInlineFormSet):
    def prev_return_values(self):
        kw_call = self.instance

        return [[
            'Vorherige Rückgabewerte',
            [
                (jsonify(None, source.pk), str(source))
                for source in
                KeywordCallParameterSource.objects
                .filter(
                    kw_call_ret_val__in=kw_call.get_previous_return_values()
                )
            ]
        ]]

    def get_variables(
            self,
            window_ids: list[int],
            system_ids: list[int],
            show: Callable[[KeywordCallParameterSource], str]
    ):
        window_variables = [[
            'Referenzwerte',
            [
                (jsonify(None, source.pk), show(source))
                for source in
                KeywordCallParameterSource.objects
                .filter(variable_value__variable__windows__in=window_ids)
                .filter(variable_value__variable__systems__in=system_ids)
                .distinct()
            ]
        ]]

        window_indep_variables = [[
            'Globale Referenzwerte',
            [
                (jsonify(None, source.pk), show(source))
                for source in
                KeywordCallParameterSource.objects.filter(
                    variable_value__variable__all_windows=True
                )
            ]
        ]]

        return window_variables + window_indep_variables

    def get_choices(self, obj: KeywordCall):
        calling_keyword = obj.from_keyword
        kw_params = [[
            'Parameter',
            [
                (jsonify(None, source.pk), str(source))
                for source in KeywordCallParameterSource.objects
                .filter(kw_param__keyword=calling_keyword)
            ]
        ]]

        return kw_params + self.prev_return_values()

    def add_fields(self, form, index):
        super().add_fields(form, index)

        class CustomSelect(forms.Select):
            template_name = 'admin/keywordcall/select.html'

            @property
            def media(self):
                self.i18n_name = get_select2_language()
                extra = "" if settings.DEBUG else ".min"
                i18n_file = (
                    ("admin/js/vendor/select2/i18n/%s.js" % self.i18n_name,)
                    if self.i18n_name
                    else ()
                )
                return forms.Media(
                    js=(
                           "admin/js/vendor/jquery/jquery%s.js" % extra,
                           "admin/js/vendor/select2/select2.full%s.js" % extra,
                       )
                       + i18n_file
                       + (
                           "admin/js/jquery.init.js",
                           "admin/js/autocomplete.js",
                       ),
                    css={
                        "screen": (
                            "admin/css/vendor/select2/select2%s.css" % extra,
                            "admin/css/autocomplete.css",
                        ),
                    },
                )

        if index is not None:
            kw_call_parameter: KeywordCallParameter = form.instance
            current_value = kw_call_parameter.value
            value, displayed_value = show_value(current_value)

            if value and displayed_value in {'True', 'False'}:
                choices = [
                    (jsonify('True', None), 'True'), 
                    (jsonify('False', None), 'False'), 
                ]
            else:
                choices = (
                        [(None, '')] +
                        [['Eingabe', [show_value(current_value)]]] +
                        self.get_choices(self.instance)
                )

            form.fields['value'] = DynamicChoiceField(
                widget=CustomSelect(
                    choices=choices,
                    attrs={
                        # Allow manual input
                        'data-tags': 'true',
                        'data-width': '60%',
                        'data-placeholder': 'Wert auswählen oder eintragen'
                    }
                )
            )

            if kw_call_parameter.parameter.is_list:
                form.fields['value'].help_text = 'Wert 1, Wert 2, ...'
