from django.contrib import admin
from django.utils.safestring import mark_safe

from ..models import KeywordCall, KeywordCallParameter


class ParameterFields:
    def show_parameter(self, kw_call: KeywordCall, position: int):
        params = list(kw_call.parameters.all())
        position0 = position - 1

        if len(params) > position0:
            param: KeywordCallParameter = params[position0]
            value = param.current_value or ''
            return mark_safe('%s<br><i style="color: gray">%s</i>' % (value, param.name))
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
