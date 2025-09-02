from django.contrib import admin

from keyta.admin.base_admin import BaseAdmin

from ..models import KeywordParameter, KeywordCallParameter


@admin.register(KeywordParameter)
class KeywordParameterAdmin(BaseAdmin):
    def get_protected_objects(self, obj):
        kw_parameter: KeywordParameter = obj

        return list(
            KeywordCallParameter.objects
            .filter(value_ref__kw_param=kw_parameter)
            .exclude(keyword_call__execution__isnull=False)
        ) + list(
            KeywordCallParameter.objects
            .filter(parameter=kw_parameter)
            .exclude(keyword_call__execution__isnull=False)
        )
