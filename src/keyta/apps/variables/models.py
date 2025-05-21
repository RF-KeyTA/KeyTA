from typing import Optional

from django.apps import apps
from django.db import models
from django.utils.translation import gettext_lazy as _

from keyta.apps.keywords.models import KeywordCallParameterSource
from keyta.models.base_model import AbstractBaseModel


class VariableType(models.TextChoices):
    DICT = 'DICT', _('Eine Instanz')
    LIST = 'LIST', _('Mehrere Instanzen')


class Variable(AbstractBaseModel):
    name = models.CharField(max_length=255, verbose_name=_('Name'))

    # Customization #
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Beschreibung')
    )
    schema = models.ForeignKey(
        'variables.VariableSchema',
        null=True,
        on_delete=models.CASCADE,
        related_name='instances',
        verbose_name=_('Vorlage')
    )
    systems = models.ManyToManyField(
        'systems.System',
        related_name='variables',
        verbose_name=_('Systeme')
    )
    type = models.CharField(
        max_length=255,
        choices=VariableType.choices,
        default=VariableType.DICT,
        verbose_name=_('Menge')
    )
    windows = models.ManyToManyField(
        'windows.Window',
        related_name='variables',
        verbose_name=_('Masken')
    )

    def __str__(self):
        return self.name

    def add_value(
            self,
            schema_field: 'AbstractVariableSchemaField',
            list_variable: Optional['AbstractVariable']=None
    ):
        VariableValue = apps.get_model('variables', 'VariableValue')
        VariableValue.objects.get_or_create(
            name=schema_field.name,
            variable=self,
            list_variable=list_variable,
            schema_field=schema_field
        )

    def delete(self, using=None, keep_parents=False):
        if self.is_list():
            for element in self.elements.all():
                element.delete()

        super().delete(using, keep_parents)

    def is_dict(self):
        return self.type == VariableType.DICT

    def is_list(self):
        return self.type == VariableType.LIST

    def to_robot(self):
        if self.is_dict():
            return (
                '&{%s}' % self.name,
                {
                    value.name: value.value
                    for value in self.values.all()
                }
            )

        if self.is_list():
            return (
                '@{%s}' % self.name,
                [
                    '${%s}' % element.variable.name
                    for element in self.elements.all()
                ]
            )

    class Meta:
        ordering = ['name']
        verbose_name = _('Referenzwert')
        verbose_name_plural = _('Referenzwerte')

        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['window', 'name'],
        #         name='unique_variable_per_window'
        #     )
        # ]


class VariableInList(AbstractBaseModel):
    index = models.PositiveSmallIntegerField(default=0)
    list_variable = models.ForeignKey(
        'variables.Variable',
        on_delete=models.CASCADE,
        related_name='elements'
    )
    variable = models.ForeignKey(
        'variables.Variable',
        on_delete=models.CASCADE,
        related_name='in_list',
        verbose_name=_('Referenzwert')
    )

    def __str__(self):
        return f'{self.list_variable.name}[{self.index}] = {self.variable.name}'

    def delete(self, using=None, keep_parents=False):
        self.variable.delete()
        return super().delete(using, keep_parents)

    class Meta:
        ordering = ['index']


class VariableValue(AbstractBaseModel):
    list_variable = models.ForeignKey(
        'variables.Variable',
        on_delete=models.CASCADE,
        null=True
    )
    schema_field = models.ForeignKey(
        'variables.VariableSchemaField',
        on_delete=models.CASCADE,
        null=True,
        related_name='uses'
    )
    variable = models.ForeignKey(
        'variables.Variable',
        on_delete=models.CASCADE,
        related_name='values'
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('Name')
    )
    value = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Wert')
    )

    def __str__(self):
        return self.name

    def current_value(self):
        return self.value

    def save(
        self, force_insert=False, force_update=False, using=None,
            update_fields=None
    ):
        if not self.pk:
            super().save(force_insert, force_update, using, update_fields)
            KeywordCallParameterSource.objects.create(variable_value=self)
        else:
            super().save(force_insert, force_update, using, update_fields)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['variable', 'name'],
                name='unique_variable_value_name'
            )
        ]
        verbose_name = _('Wert')
        verbose_name_plural = _('Werte')


class VariableSchema(AbstractBaseModel):
    windows = models.ManyToManyField(
        'windows.Window',
        related_name='schemas',
        verbose_name=_('Masken')
    )
    name = models.CharField(
        max_length=255
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Vorlage')
        verbose_name_plural = _('Vorlagen')


class VariableSchemaField(AbstractBaseModel):
    index = models.PositiveSmallIntegerField(
        default=0,
        db_index=True
    )
    schema = models.ForeignKey(
        'variables.VariableSchema',
        on_delete=models.CASCADE,
        related_name='fields'
    )
    name = models.CharField(
        max_length=255
    )

    def __str__(self):
        return self.name

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.pk:
            super().save(force_insert, force_update, using, update_fields)
            KeywordCallParameterSource.objects.create(variable_schema_field=self)

            instance: Variable
            for instance in self.schema.instances.filter(type=VariableType.DICT):
                instance.add_value(self)
        else:
            super().save(force_insert, force_update, using, update_fields)

            value: VariableValue
            for value in self.uses.all():
                value.name = self.name
                value.save()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['schema', 'name'],
                name='unique_field_per_schema'
            )
        ]
        ordering = ['index']
        verbose_name = _('Feld')
        verbose_name_plural = _('Felder')


class VariableDocumentation(Variable):
    class Meta:
        proxy = True
        verbose_name = _('Referenzwert')
        verbose_name_plural = _('Referenzwerte')


class VariableQuickAdd(Variable):
    class Meta:
        proxy = True
        verbose_name = _('Referenzwert')
        verbose_name_plural = _('Referenzwerte')


class VariableQuickChange(Variable):
    class Meta:
        proxy = True
        verbose_name = _('Referenzwert')
        verbose_name_plural = _('Referenzwerte')


class VariableSchemaQuickAdd(VariableSchema):
    class Meta:
        proxy = True
        verbose_name = _('Vorlage')
        verbose_name_plural = _('Vorlagen')


class VariableWindowRelation(AbstractBaseModel, Variable.windows.through):
    def __str__(self):
        return str(self.window)

    class Meta:
        auto_created = True
        proxy = True
        verbose_name = _('Referenzwert')
        verbose_name_plural = _('Referenzwerte')
