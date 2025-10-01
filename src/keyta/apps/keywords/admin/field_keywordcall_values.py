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
                'hx-trigger': f'modal-closed-{kw_call.pk} from:body, modal-closed from:body'
            }

            query_params = {
                'update-icon': icon.attrs['name']
            }
            if self.get_user(request):
                query_params['user'] = '1'

            htmx_attrs['hx-get'] += '?' + url_query_parameters(query_params)

            if 'None' in url:
                return link(
                    url,
                    str(icon),
                    attrs={'style': 'visibility: hidden'}
                )

            if not kw_call.to_keyword:
                return open_link_in_modal(
                    url + f'?kw_call_pk={kw_call.pk}',
                    str(icon),
                    attrs=htmx_attrs | {'style': 'visibility: hidden'}
                )

            return open_link_in_modal(
                url + f'?kw_call_pk={kw_call.pk}',
                str(icon),
                attrs=htmx_attrs
            )

        KeywordCallValuesField.values = values

        return super().get_readonly_fields(request, obj) + [self.name]

    def get_user(self, request):
        pass
