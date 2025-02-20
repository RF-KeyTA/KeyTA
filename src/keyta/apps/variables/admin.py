from django.contrib import admin

from keyta.admin.base_admin import BaseAdmin, BaseAddAdmin
from keyta.admin.variable import BaseVariableAdmin, Values

from apps.variables.models import Variable, VariableValue, VariableWindow, WindowVariable


@admin.register(Variable)
class VariableAdmin(BaseVariableAdmin):
    pass


@admin.register(VariableValue)
class VariableValueAdmin(BaseAdmin):
    pass


@admin.register(VariableWindow)
class VariableWindowAdmin(BaseAdmin):
    pass


@admin.register(WindowVariable)
class WindowVariableAdmin(BaseAddAdmin):
    inlines = [Values]
