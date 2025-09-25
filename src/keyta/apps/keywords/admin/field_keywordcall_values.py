from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from keyta.widgets import link, open_link_in_modal, url_query_parameters

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
            icon.attrs['style'] |= {'margin-left': '5px'}
            url = kw_call.get_admin_url()

            htmx_attrs = {
                'hx-get': url,
                'hx-on::after-swap': 'presentRelatedObjectModal()',
                'hx-swap': 'innerHTML',
                'hx-trigger': 'modal-closed from:body, step-changed from:body'
            }

            query_params = {
                'update_icon': icon.attrs['name']
            }
            if self.get_user(request):
                query_params['user'] = '1'

            htmx_attrs['hx-get'] += '?' + url_query_parameters(query_params)

            if 'None' in url:
                return link(
                    url,
                    str(icon)
                )

            return open_link_in_modal(
                url,
                str(icon),
                htmx_attrs
            )

        KeywordCallValuesField.values = values

        return super().get_readonly_fields(request, obj) + [self.name]

    def get_user(self, request):
        pass
