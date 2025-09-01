from django.contrib import admin

from keyta.admin.base_admin import BaseAdmin

from ..models import VariableValue


@admin.register(VariableValue)
class VariableValueAdmin(BaseAdmin):
    pass
