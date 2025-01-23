from django.contrib import admin
from django.utils.translation import gettext as _

from apps.common.admin import SortableTabularInlineWithDelete

from apps.common.widgets import open_link_in_modal

from ..forms import StepsForm
from ..models import KeywordCall


class StepsInline(SortableTabularInlineWithDelete):
    model = KeywordCall
    fields = ['to_keyword', 'args']
    form = StepsForm
    readonly_fields = ['args']
    extra = 1  # Must be > 0 in order for SequenceSteps to work

    @admin.display(description=_('Werte'))
    def args(self, obj):
        kw_call: KeywordCall = obj

        if not kw_call.pk:
            return '-'

        if kw_call.has_empty_arg():
            return open_link_in_modal(
                kw_call.get_admin_url(),
                '<i class=" error-duotone fa-solid fa-list" style="font-size: 36px;"></i>'
            )
        else:
            return open_link_in_modal(
                kw_call.get_admin_url(),
                '<i class=" fa-solid fa-list" style="font-size: 36px"></i>'
            )
