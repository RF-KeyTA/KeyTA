from django.contrib import admin
from django.db.models import Q

from keyta.admin.base_admin import BaseAdmin
from keyta.apps.keywords.models import KeywordCallParameter

from ..models import VariableValue


@admin.register(VariableValue)
class VariableValueAdmin(BaseAdmin):
    def get_protected_objects(self, obj):
        variable_value: VariableValue = obj

        return list(
            KeywordCallParameter.objects.filter(
                Q(value_ref__variable_value=variable_value) |
                Q(value_ref__table_column=variable_value.variable)
            )
        )
