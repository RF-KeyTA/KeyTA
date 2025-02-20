from ..models import WindowKeywordParameter
from .keyword_parameters_inline import ParametersInline


class WindowKeywordParameters(ParametersInline):
    model = WindowKeywordParameter
