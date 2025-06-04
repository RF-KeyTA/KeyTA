from typing import Optional

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from keyta.widgets import Icon, open_link_in_modal

from ..models import KeywordCall


class BaseKeywordCallArgs:
    def get_icon(self, kw_call: KeywordCall, user: Optional[AbstractUser]=None):
        if any([
            not kw_call.pk,
            not kw_call.to_keyword,
            # For a Library/Resource keyword without parameters the icon is necessary to set the return value
            not kw_call.to_keyword.parameters.exists()
            and not kw_call.to_keyword.return_values.exists()
            and not any([kw_call.to_keyword.library, kw_call.to_keyword.resource]),
        ]):
            return '-'

        if self.invalid_keyword_call_args(kw_call, user):
            icon = Icon(
                settings.FA_ICONS.kw_call_parameters,
                {'filter': 'hue-rotate(150deg)'}
            )

            return open_link_in_modal(
                kw_call.get_admin_url() + '?empty_args=1',
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

    def invalid_keyword_call_args(self, kw_call: KeywordCall, user: Optional[AbstractUser]=None) -> bool:
        if kw_call.parameters.count() != kw_call.to_keyword.parameters.count():
            kw_call.update_parameters(user)
        
        return kw_call.has_empty_arg(user)


class KeywordCallArgsField(BaseKeywordCallArgs):
    @admin.display(description=_('Werte'))
    def args(self, kw_call: KeywordCall):
        return super().get_icon(kw_call)

    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj) + ['args']

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj) + ['args']
