from django.utils.translation import gettext as _

from keyta.admin.base_inline import SortableTabularInlineWithDelete

from ..models import KeywordParameter


class ParametersInline(SortableTabularInlineWithDelete):
    model = KeywordParameter
    fields = ['position', 'name']
    extra = 0
    verbose_name = _('Parameter')
    verbose_name_plural = _('Parameters')
