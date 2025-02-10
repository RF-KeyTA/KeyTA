from keyta.apps.keywords.admin import ReturnValueInline

from ..models import WindowKeywordReturnValue


class WindowKeywordReturnValues(ReturnValueInline):
    model = WindowKeywordReturnValue
