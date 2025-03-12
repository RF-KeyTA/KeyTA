from django.contrib import admin

from keyta.admin.base_admin import BaseAdmin
from keyta.admin.variable import (
    BaseVariableAdmin,
    BaseVariableDocumentationAdmin,
    BaseVariableQuickAddAdmin,
    BaseVariableQuickChangeAdmin,
    BaseVariableSchemaAdmin,
    BaseVariableSchemaQuickAddAdmin,
)

from .models import (
    Variable,
    VariableDocumentation,
    VariableInList,
    VariableQuickAdd,
    VariableQuickChange,
    VariableSchema,
    VariableSchemaField,
    VariableSchemaQuickAdd,
    VariableValue,
    VariableWindowRelation,
)


@admin.register(Variable)
class VariableAdmin(BaseVariableAdmin):
    pass


@admin.register(VariableDocumentation)
class VariableDocumentationAdmin(BaseVariableDocumentationAdmin):
    pass


@admin.register(VariableInList)
class VariableInListAdmin(BaseAdmin):
    pass


@admin.register(VariableQuickAdd)
class VariableQuickAddAdmin(BaseVariableQuickAddAdmin):
    pass


@admin.register(VariableQuickChange)
class VariableQuickChangeAdmin(BaseVariableQuickChangeAdmin):
    pass


@admin.register(VariableSchema)
class VariableSchemaAdmin(BaseVariableSchemaAdmin):
    pass


@admin.register(VariableSchemaField)
class VariableSchemaFieldAdmin(BaseAdmin):
    pass


@admin.register(VariableSchemaQuickAdd)
class VariableSchemaQuickAddAdmin(BaseVariableSchemaQuickAddAdmin):
    pass


@admin.register(VariableValue)
class VariableValueAdmin(BaseAdmin):
    pass


@admin.register(VariableWindowRelation)
class VariableWindowAdmin(BaseAdmin):
    pass
