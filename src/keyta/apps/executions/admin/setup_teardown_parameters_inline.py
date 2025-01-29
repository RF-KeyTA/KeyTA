from keyta.apps.keywords.admin import KeywordCallParametersInline
from keyta.apps.keywords.forms import KeywordCallParameterFormset


class SetupTeardownParameterFormset(KeywordCallParameterFormset):
    def get_choices(self, obj):
        return []


class SetupTeardownParametersInline(KeywordCallParametersInline):
    formset = SetupTeardownParameterFormset
