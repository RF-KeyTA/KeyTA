from typing import Optional

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _

from keyta.widgets import Icon, open_link_in_modal

from ..models import KeywordCall


class BaseKeywordCallArgs:
    def get_icon(self, kw_call: KeywordCall, user: Optional[AbstractUser]=None):
        if not kw_call.pk:
            return '-'
        
        if (kw_call.parameters.count() != kw_call.to_keyword.parameters.count() or
            kw_call.has_empty_arg(user)
        ):
            icon = Icon(
                settings.FA_ICONS.kw_call_parameters,
                {'filter': 'hue-rotate(150deg)'}
            )

            return open_link_in_modal(
                kw_call.get_admin_url(),
                str(icon)
            )
        else:
            icon = Icon(
                settings.FA_ICONS.kw_call_parameters
            )

            return open_link_in_modal(
                kw_call.get_admin_url(),
                str(icon)
            )


class KeywordCallArgsField(BaseKeywordCallArgs):
    @admin.display(description=_('Werte'))
    def args(self, kw_call: KeywordCall):
        return super().get_icon(kw_call)

    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj) + ['args']

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj) + ['args']
