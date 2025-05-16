from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..models import KeywordCall


class FirstParameterField:
    @admin.display(description=_('1. Parameter'))
    def first_parameter(self, kw_call: KeywordCall):
        if current_value := kw_call.parameters.first().current_value:
            return current_value
        else:
            return '-'

    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj) + ['first_parameter']

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj) + ['first_parameter']
