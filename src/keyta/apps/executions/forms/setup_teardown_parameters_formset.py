from django.db.models import QuerySet

from keyta.apps.keywords.forms import KeywordCallParameterFormset
from keyta.apps.keywords.forms.keywordcall_parameter_formset import get_global_variables
from keyta.apps.keywords.models import KeywordCall


class SetupTeardownParametersFormset(KeywordCallParameterFormset):
    def get_ref_choices(self, kw_call: KeywordCall):
        execution = kw_call.execution
        systems = QuerySet()

        if keyword := execution.keyword:
            systems = keyword.systems

        if testcase := execution.testcase:
            systems = testcase.systems

        system_ids = list(systems.values_list('id', flat=True))

        return get_global_variables(system_ids)
