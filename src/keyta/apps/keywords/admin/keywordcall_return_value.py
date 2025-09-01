from django.contrib import admin

from keyta.admin.base_admin import BaseAdmin

from ..models import KeywordCallReturnValue, KeywordCallParameter


# This admin is necessary in order to delete a KeywordCallReturnValue
@admin.register(KeywordCallReturnValue)
class KeywordCallReturnValueAdmin(BaseAdmin):
    fields = ['return_value_name']

    def get_protected_objects(self, obj):
        kw_call_return_value: KeywordCallReturnValue = obj

        return (
            list(kw_call_return_value.uses.all()) +
            list(
                KeywordCallParameter.objects
                .filter(value_ref__kw_call_ret_val=kw_call_return_value)
            )
        )

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description='Name')
    def return_value_name(self, kw_call_return_value: KeywordCallReturnValue):
        return str(kw_call_return_value)
