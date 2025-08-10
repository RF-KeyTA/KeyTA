import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from keyta.widgets import BaseSelect

from ..json_value import JSONValue


class DynamicChoiceField(forms.CharField):
    def clean(self, value):
        return self.to_python(value)

    def has_changed(self, initial, data):
        return super().has_changed(initial, data)

    def to_python(self, value: str):
        if value is None:
            raise ValidationError(self.default_error_messages['required'])

        if value.startswith('{') and value.endswith('}'):
            return value

        return JSONValue(
            arg_name=None,
            kw_call_index=None,
            pk=None,
            user_input=re.sub(r"\s{2,}", " ", value)
        ).jsonify()


class UserInputFormset(forms.BaseInlineFormSet):
    empty_input = None, _('Kein Wert')
    json_field_name = 'value'

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
        # Calculate the choices once
        self.choices = self.get_choices(instance)
        self.parent = instance

    def add_fields(self, form, index):
        super().add_fields(form, index)

        user_input_value, user_input_show = self.get_user_input(form, index)

        if user_input_show in {"True", "False"}:
            true_json_value = JSONValue(
                arg_name=None,
                kw_call_index=None,
                pk=None,
                user_input='True',
            ).jsonify()

            false_json_value = JSONValue(
                arg_name=None,
                kw_call_index=None,
                pk=None,
                user_input='False',
            ).jsonify()

            user_input_choices = [
                (true_json_value, "True"),
                (false_json_value, "False")
            ]
        else:
            user_input_choices = [(user_input_value, user_input_show)]

        choices = (
            [(None, _('Kein Wert'))] +
            [[_('Eingabe'), user_input_choices]] +
            self.choices
        )

        self.form_errors(form)

        form.fields[self.json_field_name] = DynamicChoiceField(
            widget=BaseSelect(
                _('Wert auswählen oder eintragen'),
                choices=choices,
                attrs={
                    # Allow manual input
                    'data-tags': 'true',
                }
            )
        )

    def form_errors(self, form):
        pass

    def get_choices(self, parent) -> list:
        pass

    def get_json_value(self, form) -> JSONValue:
        pass

    def get_user_input(self, form, index):
        # The index of an extra form is None
        if index is not None:
            json_value: JSONValue = self.get_json_value(form)

            if json_value and not json_value.pk:
                user_input = json_value.user_input
                if not user_input:
                    return self.empty_input
                else:
                    return json_value.jsonify(), user_input

        return self.empty_input
