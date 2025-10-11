from django.contrib import admin
from django.db.models import Q

from keyta.admin.base_admin import BaseAdmin

from ..models import KeywordParameter, KeywordCallParameter


@admin.register(KeywordParameter)
class KeywordParameterAdmin(BaseAdmin):
    def get_protected_objects(self, obj):
        kw_parameter: KeywordParameter = obj
        uses = (
            KeywordCallParameter.objects
            .filter(Q(value_ref__kw_param=kw_parameter) | Q(parameter=kw_parameter))
            .exclude(keyword_call__execution__isnull=False)
        )

        if uses.count() > 1:
            return list(uses)

        return []
