import re

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from keyta.widgets import BaseSelect

from ..json_value import JSONValue
from ..models import KeywordCall, KeywordCallParameterSource
from ..models.keywordcall_parameter_source import KeywordCallParameterSourceType


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


empty_input = JSONValue(
    arg_name=None,
    kw_call_index=None,
    pk=None,
    user_input='${EMPTY}'
).jsonify(), _('leer')

no_input = None, _('Kein Wert')


class UserInputSelect(BaseSelect):
    icons = {
        KeywordCallParameterSourceType.KEYWORD_PARAMETER: settings.FA_ICONS.arg_kw_param,
        KeywordCallParameterSourceType.KW_CALL_RETURN_VALUE: settings.FA_ICONS.arg_return_value,
        KeywordCallParameterSourceType.VARIABLE_VALUE: settings.FA_ICONS.arg_variable_value,
    }

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)

        if value:
            json_value = JSONValue.from_json(value)

            if json_value.pk:
                source = KeywordCallParameterSource.objects.get(pk=json_value.pk)
                icon = self.icons[source.type]

                if variable_value := source.variable_value:
                    if variable_value.variable.template:
                        icon = settings.FA_ICONS.arg_template_variable_value

                option['attrs'].update({'icon': icon})

        return option


def user_input_field(placeholder: str, user_input: tuple, choices: list = None):
    return DynamicChoiceField(
        widget=UserInputSelect(
            placeholder,
            choices=(
                [(None, _('Kein Wert'))] +
                [[_('Eingabe'), [user_input, empty_input]]] +
                (choices or [])
            ),
            attrs={
                # Allow manual input
                'data-tags': 'true',
            }
        )
    )


class UserInputFormset(forms.BaseInlineFormSet):
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
            self.typedocs = library.get_typedocs()

    def get_json_value(self, form) -> JSONValue:
        pass

    def get_ref_choices(self, parent) -> list:
        pass

    def get_user_input(self, form, index):
        json_value: JSONValue = self.get_json_value(form)

        if json_value and not json_value.pk:
            user_input = json_value.user_input

            if user_input and user_input != '${EMPTY}':
                return json_value.jsonify(), user_input

        return no_input
