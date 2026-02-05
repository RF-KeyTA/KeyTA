from keyta.apps.keywords.models.keywordcall_parameters import KeywordCallParameter
from keyta.apps.keywords.json_value import JSONValue


class LibraryKeywordCallParameter(KeywordCallParameter):
    def reset_value(self):
        self.value = JSONValue(
            arg_name=None,
            kw_call_index=None,
            pk=None,
            user_input=self.parameter.default_value
        ).jsonify()
        self.save()

    class Meta:
        proxy = True
