from typing import Optional

from django.utils.translation import gettext as _

from keyta.models.base_model import AbstractBaseModel
from keyta.models.variable import (
    AbstractVariable,
    AbstractVariableSchema,
    AbstractVariableSchemaField,
    AbstractVariableValue,
    AbstractVariableInList
)


class Variable(AbstractVariable):
    def add_value(
            self,
            schema_field: AbstractVariableSchemaField,
            list_variable: Optional[AbstractVariable]=None
    ):
        VariableValue.objects.get_or_create(
            name=schema_field.name,
            variable=self,
            list_variable=list_variable,
            schema_field=schema_field
        )


class VariableDocumentation(Variable):
    class Meta:
        proxy = True
        verbose_name = _('Referenzwert')
        verbose_name_plural = _('Referenzwerte')


class VariableInList(AbstractVariableInList):
    pass


class VariableQuickAdd(Variable):
    class Meta:
        proxy = True
        verbose_name = _('Referenzwert')
        verbose_name_plural = _('Referenzwerte')


class VariableSchema(AbstractVariableSchema):
    pass


class VariableSchemaField(AbstractVariableSchemaField):
    pass


class VariableSchemaQuickAdd(VariableSchema):
    class Meta:
        proxy = True
        verbose_name = _('Vorlage')
        verbose_name_plural = _('Vorlagen')


class VariableValue(AbstractVariableValue):
    pass


class VariableWindowRelation(AbstractBaseModel, Variable.windows.through):
    def __str__(self):
        return str(self.window)

    class Meta:
        auto_created = True
        proxy = True
        verbose_name = _('Beziehung zu Maske')
        verbose_name_plural = _('Beziehungen zu Masken')
