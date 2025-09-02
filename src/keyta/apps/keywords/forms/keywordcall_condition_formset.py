from django.utils.translation import gettext_lazy as _

from keyta.widgets import BaseSelect

from ..json_value import JSONValue
from ..models import KeywordCall, KeywordCallParameterSource, KeywordCallCondition
from ..models.keywordcall_condition import ConditionChoices
from .keywordcall_parameter_formset import get_keyword_parameters
from .user_input_formset import UserInputFormset, user_input_field


class KeywordCallConditionFormset(UserInputFormset):
    empty_input = JSONValue(
        arg_name=None,
        kw_call_index=None,
        pk=None,
        user_input=''
    ).jsonify(), _('leer')

    def add_fields(self, form, index):
        super().add_fields(form, index)

        kw_call: KeywordCall = self.parent
        kw_parameters = KeywordCallParameterSource.objects.filter(kw_param__in=kw_call.from_keyword.parameters.all())
        previous_return_values = KeywordCallParameterSource.objects.filter(kw_call_ret_val__in=kw_call.get_previous_return_values())

        parameters = []
        if kw_parameters.exists():
            parameters = [[
                _('Parameters'),
                [(source.pk, str(source)) for source in kw_parameters]
            ]]

        return_values = []
        if previous_return_values.exists():
            return_values = [[
                _('Vorherige Rückgabewerte'),
                [(source.pk, str(source)) for source in previous_return_values]
            ]]

        form.fields['value_ref'].widget = BaseSelect(
            _('Wert auswählen'),
            choices=(
                [(None, '')] +
                parameters +
                return_values
            )
        )

        form.fields['condition'].widget = BaseSelect(
            _('Bedingung auswählen'),
            choices=[(None, '')] + ConditionChoices.choices
        )

        form.fields['expected_value'] = user_input_field(
            _('Wert auswählen oder eintragen'),
            self.get_user_input(form, index),
            choices=self.ref_choices
        )

    def get_ref_choices(self, kw_call: KeywordCall):
        return get_keyword_parameters(kw_call)

    def get_json_value(self, form):
        kw_call_condition: KeywordCallCondition = form.instance

        if kw_call_condition.expected_value:
            return JSONValue.from_json(kw_call_condition.expected_value)
