from django.contrib import admin

from keyta.admin.base_admin import BaseAdmin

from ..models import KeywordCallReturnValue


# This admin is necessary in order to delete a KeywordCallReturnValue
@admin.register(KeywordCallReturnValue)
class KeywordCallReturnValueAdmin(BaseAdmin):
    fields = ['return_value_name']

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description='Name')
    def return_value_name(self, kw_call_return_value: KeywordCallReturnValue):
        return str(kw_call_return_value)
