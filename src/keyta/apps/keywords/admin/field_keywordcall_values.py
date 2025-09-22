from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.admin.base_admin import url_params
from keyta.widgets import open_link_in_modal

from ..models import KeywordCall


class KeywordCallValuesField:
    name = 'values'

    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj) + [self.name]

    def get_kw_call(self, obj):
        return obj

    def get_readonly_fields(self, request, obj=None):
        @admin.display(description=_('Werte'))
        def values(self, obj):
            kw_call: KeywordCall = self.get_kw_call(obj)
            icon = kw_call.get_icon(self.get_user(request))
            htmx_attrs = {
                'hx-get': kw_call.get_admin_url(),
                'hx-on::after-swap': 'presentRelatedObjectModal()',
                'hx-swap': 'innerHTML',
                'hx-trigger': 'modal-closed from:body'
            }

            query_params = {
                'update_icon': icon.attrs['name']
            }
            if self.get_user(request):
                query_params['user'] = '1'

            htmx_attrs['hx-get'] += '?' + url_params(query_params)

            return open_link_in_modal(
                kw_call.get_admin_url(),
                str(icon),
                htmx_attrs
            )

        KeywordCallValuesField.values = values

        return super().get_readonly_fields(request, obj) + [self.name]

    def get_user(self, request):
        pass
