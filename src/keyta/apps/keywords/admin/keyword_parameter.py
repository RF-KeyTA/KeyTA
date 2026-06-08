from django.contrib import admin

from keyta.admin.base_admin import BaseAdmin

from ..models import KeywordParameter, KeywordCallParameter


@admin.register(KeywordParameter)
class KeywordParameterAdmin(BaseAdmin):
    def get_protected_objects(self, parameter: KeywordParameter):
        return (
            KeywordCallParameter.objects
            .filter(keyword_call__from_keyword=parameter.keyword, value_ref__kw_param=parameter)
            .distinct()
        )
