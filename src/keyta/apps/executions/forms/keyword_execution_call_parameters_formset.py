from keyta.apps.keywords.forms import KeywordCallParameterFormset
from keyta.apps.keywords.models import KeywordCall


class KeywordCallExecutionParameterFormset(KeywordCallParameterFormset):
    def get_choices(self, obj):
        kw_call: KeywordCall = obj
        keyword = kw_call.execution.keyword
        window_ids = list(keyword.windows.values_list('id', flat=True))
        system_ids = list(keyword.systems.values_list('id', flat=True))

        return self.get_window_variables(
            window_ids,
            system_ids,
            lambda value_ref: str(value_ref)
        )
