from django.contrib import admin

from keyta.admin.base_admin import BaseAdmin

from ..models import KeywordReturnValue, KeywordCallParameter


@admin.register(KeywordReturnValue)
class ReturnValueAdmin(BaseAdmin):
    def get_protected_objects(self, obj):
        return_value: KeywordReturnValue = obj

        return (
            list(
                KeywordCallParameter.objects
                .filter(value_ref__kw_call_ret_val__return_value=return_value)
            )
        )
