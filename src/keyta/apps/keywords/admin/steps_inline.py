from django.conf import settings
from django.contrib import admin
from django.http import HttpRequest
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_inline import DeleteRelatedField, SortableTabularInline
from keyta.widgets import Icon

from ..forms import StepsForm
from ..models import Keyword, KeywordCall
from .field_parameters import ParameterFields
from .field_keywordcall_args import KeywordCallArgsField


class StepsInline(
    DeleteRelatedField,
    ParameterFields,
    KeywordCallArgsField,
    SortableTabularInline
):
    model = KeywordCall
    fk_name = 'from_keyword'
    fields = ['to_keyword']
    form = StepsForm
    extra = 0

    def get_fields(self, request, obj=None):
        keyword: Keyword = obj

        if keyword and keyword.calls.filter(conditions__isnull=False).exists():
            return ['condition'] + super().get_fields(request, obj)

        return super().get_fields(request, obj)

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        @admin.display(description='')
        def condition(self, kw_call: KeywordCall):
            if kw_call.conditions.exists():
                return mark_safe(str(Icon(
                    settings.FA_ICONS.condition,
                    {
                        'font-size': '18px',
                        'margin-top': '14px'
                    },
                    title=_('Vorbedingung')
                )))

            return ''

        StepsInline.condition = condition

        return ['condition'] + readonly_fields

    def has_delete_permission(self, request, obj=None):
        keyword: Keyword = obj

        if keyword and keyword.is_action:
            return self.can_change(request.user, 'action')

        if keyword and keyword.is_sequence:
            self.can_change(request.user, 'sequence')

        return super().has_delete_permission(request, obj)
