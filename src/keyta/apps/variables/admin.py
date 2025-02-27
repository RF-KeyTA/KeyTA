from django.contrib import admin

from keyta.admin.base_admin import BaseAdmin
from keyta.admin.variable import (
    BaseVariableAdmin,
    BaseVariableQuickAddAdmin,
    BaseVariableSchemaAdmin,
    BaseVariableSchemaQuickAddAdmin,
)

from .models import (
    Variable,
    VariableInList,
    VariableQuickAdd,
    VariableSchema,
    VariableSchemaField,
    VariableSchemaQuickAdd,
    VariableValue,
    VariableWindowRelation
)


@admin.register(Variable)
class VariableAdmin(BaseVariableAdmin):
    pass


@admin.register(VariableSchema)
class VariableSchemaAdmin(BaseVariableSchemaAdmin):
    pass


@admin.register(VariableSchemaField)
class VariableSchemaFieldAdmin(BaseAdmin):
    pass


@admin.register(VariableValue)
class VariableValueAdmin(BaseAdmin):
    pass


@admin.register(VariableWindowRelation)
class VariableWindowAdmin(BaseAdmin):
    pass


@admin.register(VariableQuickAdd)
class VariableQuickAddAdmin(BaseVariableQuickAddAdmin):
    pass


@admin.register(VariableSchemaQuickAdd)
class VariableSchemaQuickAddAdmin(BaseVariableSchemaQuickAddAdmin):
    pass


@admin.register(VariableInList)
class VariableInListAdmin(BaseAdmin):
    pass
