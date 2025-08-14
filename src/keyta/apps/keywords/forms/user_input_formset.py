import json
import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from keyta.widgets import BaseSelect

from ..json_value import JSONValue
from ..models import KeywordCall


def invert_dictionary(dictionary):
    return {
        value: key
        for key, value in dictionary.items()
    }


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


def user_input_field(placeholder: str, user_input: tuple, choices: list = None):
    return DynamicChoiceField(
        widget=BaseSelect(
            placeholder,
            choices=(
                [(None, _('Kein Wert'))] +
                [[_('Eingabe'), [user_input]]] +
                (choices or [])
            ),
            attrs={
                # Allow manual input
                'data-tags': 'true',
            }
        )
    )


class UserInputFormset(forms.BaseInlineFormSet):
    empty_input = None, _('Kein Wert')

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
        self.ref_choices = self.get_ref_choices(instance)
        self.enable_user_input = True
        self.parent: KeywordCall = instance
        if library := self.parent.to_keyword.library:
            self.typedocs: dict = json.loads(library.typedocs)

    def get_json_value(self, form) -> JSONValue:
        pass

    def get_ref_choices(self, parent) -> list:
        pass

    def get_user_input(self, form, index):
        json_value: JSONValue = self.get_json_value(form)

        if json_value and not json_value.pk:
            user_input = json_value.user_input
            if not user_input:
                return self.empty_input
            else:
                return json_value.jsonify(), user_input

        return self.empty_input
