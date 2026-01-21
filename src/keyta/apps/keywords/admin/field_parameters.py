from django.contrib import admin
from django.utils.safestring import mark_safe

from keyta.widgets import attrs_to_string

from ..models import KeywordCall


class ParameterFields:
    def show_parameter(self, kw_call: KeywordCall, position: int):
        pk = kw_call.pk
        htmx_attrs = {
            'hx-get': kw_call.get_admin_url(),
            'hx-swap': 'innerHTML',
            'hx-trigger': f'modal-closed-{pk} from:body, modal-closed from:body'
        }
        position0 = position - 1

        if param := kw_call.get_parameter(position0):
            name, value = param

            if value is None:
                value = ''

            if value == '${None}':
                value = 'None'

            htmx_attrs['hx-get'] += f'?update-param={position0}'

            return mark_safe(f"""
            <span {attrs_to_string(htmx_attrs)}>{value}</span>
            <br>
            <i style="color: gray">{name}</i>
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
