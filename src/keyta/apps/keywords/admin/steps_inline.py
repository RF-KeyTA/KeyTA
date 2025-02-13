from django.contrib import admin
from django.utils.translation import gettext as _

from keyta.admin.base_inline import SortableTabularInlineWithDelete


from ..forms import StepsForm
from ..models import KeywordCall
from .keywordcall_args_field import KeywordCallArgsField


class StepsInline(KeywordCallArgsField, SortableTabularInlineWithDelete):
    model = KeywordCall
    fields = ['to_keyword', 'args']
    form = StepsForm
    readonly_fields = ['args']
    extra = 1  # Must be > 0 in order for SequenceSteps to work

    @admin.display(description=_('Werte'))
    def args(self, kw_call: KeywordCall):
        if not kw_call.pk:
            return '-'
        else:
            return super().args(kw_call)
