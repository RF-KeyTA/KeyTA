from ..json_value import JSONValue
from ..models import KeywordCall, KeywordCallParameter
from .user_input_formset import UserInputFormset


class KeywordCallVarargFormset(UserInputFormset):
    def get_choices(self, kw_call: KeywordCall):
        return []

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
