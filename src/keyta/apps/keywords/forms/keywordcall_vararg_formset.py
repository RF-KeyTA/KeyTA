import json

from django.utils.translation import gettext_lazy as _

from ..json_value import JSONValue
from ..models import KeywordCall, KeywordCallParameter
from .keywordcall_parameter_formset import get_keyword_parameters, get_prev_return_values
from .user_input_formset import UserInputFormset

def user_input(input: str):
    return JSONValue(
            arg_name=None,
            kw_call_index=None,
            pk=None,
            user_input=input,
        ).jsonify()


class KeywordCallVarargFormset(UserInputFormset):
    def get_choices(self, form, index) -> list:
        kw_call_parameter: KeywordCallParameter = form.instance

        if kw_call_parameter.pk:
            parameter_type: list = json.loads(kw_call_parameter.parameter.typedoc)
            choices = dict()

            for type_ in parameter_type:
                if type_ in {'int', 'str'}:
                    self.enable_user_input = True

                if typedoc := self.typedocs.get(type_):
                    if typedoc['type'] == 'Enum':
                        self.enable_user_input = False

                        for member in typedoc['members']:
                            if member.lower() not in {'true', 'false'}:
                                choices[user_input(member)] = member

            if self.enable_user_input:
                return [[_('Eingabe'), [self.get_user_input(form, index)] + list(choices.items())]]

            return list(choices.items())

        return super().get_choices(form, index)

    def get_ref_choices(self, kw_call: KeywordCall):
        return get_keyword_parameters(kw_call) + get_prev_return_values(kw_call)

    def get_json_value(self, form):
        kw_call_parameter: KeywordCallParameter = form.instance

        if not kw_call_parameter.value:
            return JSONValue(
                arg_name=None,
                kw_call_index=None,
                pk=None,
                user_input=''
            )

        return kw_call_parameter.json_value
