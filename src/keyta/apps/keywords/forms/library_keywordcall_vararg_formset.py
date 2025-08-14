from ..json_value import JSONValue
from ..models import KeywordCallParameter
from .library_keywordcall_parameter_formset import LibraryKeywordCallParameterFormset


class LibraryKeywordCallVarargFormset(LibraryKeywordCallParameterFormset):
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
