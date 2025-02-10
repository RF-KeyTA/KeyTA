from keyta.apps.keywords.admin import ParametersInline

from ..models import WindowKeywordParameter


class WindowKeywordParameters(ParametersInline):
    model = WindowKeywordParameter
