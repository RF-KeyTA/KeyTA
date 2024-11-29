from apps.keywords.admin.keyword_parameters_inline import Parameters
from apps.windows.models import WindowKeywordParameter


class WindowKeywordParameters(Parameters):
    model = WindowKeywordParameter
