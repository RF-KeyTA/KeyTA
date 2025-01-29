from keyta.apps.keywords.admin import ReturnValueInline
from apps.windows.models import WindowKeywordReturnValue


class WindowKeywordReturnValues(ReturnValueInline):
    model = WindowKeywordReturnValue
