from django.contrib import admin
from django.utils.safestring import mark_safe

from keyta.widgets import attrs_to_string

from ..models import KeywordCall, KeywordCallParameter


class ParameterFields:
    def show_parameter(self, kw_call: KeywordCall, position: int):
        htmx_attrs = {
            'hx-get': kw_call.get_admin_url(),
            'hx-swap': 'innerHTML',
            'hx-trigger': 'modal-closed from:body'
        }
        params = list(kw_call.parameters.all())
        position0 = position - 1

        if len(params) > position0:
            param: KeywordCallParameter = params[position0]
            value = param.current_value or ''
            htmx_attrs['hx-get'] += '?update-param=' + param.name

            return mark_safe(f"""
            <span {attrs_to_string(htmx_attrs)}>{value}</span>
            <br>
            <i style="color: gray">{param.name}</i>
            """)
        else:
            return ''

    @admin.display(description='')
    def parameter1(self, kw_call: KeywordCall):
        return self.show_parameter(kw_call, 1)

    @admin.display(description='')
    def parameter2(self, kw_call: KeywordCall):
        return self.show_parameter(kw_call, 2)

    @admin.display(description='')
    def parameter3(self, kw_call: KeywordCall):
        return self.show_parameter(kw_call, 3)

    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj) + ['parameter1', 'parameter2', 'parameter3']

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj) + ['parameter1', 'parameter2', 'parameter3']
