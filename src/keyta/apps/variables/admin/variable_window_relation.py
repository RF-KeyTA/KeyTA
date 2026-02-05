from django.contrib import admin
from django.db.models import Q

from keyta.admin.base_admin import BaseAdmin
from keyta.apps.keywords.models import KeywordCallParameter

from ..models import VariableWindowRelation


@admin.register(VariableWindowRelation)
class VariableWindowAdmin(BaseAdmin):
    def get_protected_objects(self, obj):
        variable_window: VariableWindowRelation = obj

        return list(
            KeywordCallParameter.objects
            .filter(keyword_call__window=variable_window.window)
            .filter(Q(value_ref__variable_value__variable=variable_window.variable) |
                    Q(value_ref__table_column__table=variable_window.variable))
            .exclude(keyword_call__execution__isnull=False)
        )
