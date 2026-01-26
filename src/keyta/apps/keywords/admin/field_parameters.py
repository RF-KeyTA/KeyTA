from django.contrib import admin
from django.utils.safestring import mark_safe

from keyta.widgets import attrs_to_string

from ..models import KeywordCall


def repr_param(param):
    icon = param['icon']
    name = param['name']
    value = param['value']

    if value is None:
        value = len(name)*'&nbsp;'

    if value == '${None}':
        value = 'None'

    value_span = f'<span class="input-group-text bg-white" style="border-color: var(--keyta-primary-color)">{value}</span>'
    
    if icon:
        html = f"""
        <span class="input-group-prepend">
            <span class="{icon} input-group-text" style="align-content: center; background-color: var(--keyta-primary-color); border-color: var(--keyta-primary-color)"></span>
        </span>
        <span class="input-group-append">
            {value_span}
        </span>
        """
    else:
        html = value_span

    return f"""
        <span class="input-group flex-nowrap">
            {html}
        </span>
        <i style="color: gray">{name}</i>
    """


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
            htmx_attrs['hx-get'] += f'?update-param={position0}'

            return mark_safe(f"""
            <span {attrs_to_string(htmx_attrs)}>
                {repr_param(param)}
            </span>
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
