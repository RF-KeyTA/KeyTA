from keyta.apps.keywords.admin import ParametersInline
from apps.windows.models import WindowKeywordParameter


class WindowKeywordParameters(ParametersInline):
    model = WindowKeywordParameter
