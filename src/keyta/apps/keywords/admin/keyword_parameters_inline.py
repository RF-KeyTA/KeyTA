from apps.common.admin.base_inline import SortableTabularInlineWithDelete

from ..models import KeywordParameter


class Parameters(SortableTabularInlineWithDelete):
    model = KeywordParameter
    fields = ['name']
    extra = 0
    verbose_name = 'Parameter'
    verbose_name_plural = 'Parameter'
