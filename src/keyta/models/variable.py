from typing import Optional

from django.apps import apps
from django.db import models
from django.utils.translation import gettext as _

from keyta.apps.keywords.models import KeywordCallParameterSource

from .base_model import AbstractBaseModel


class VariableType(models.TextChoices):
    DICT = 'DICT', _('Eine Instanz')
    LIST = 'LIST', _('Mehrere Instanzen')


class AbstractVariable(AbstractBaseModel):
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
                element.variable.delete()
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
        abstract = True
        verbose_name = _('Referenzwert')
        verbose_name_plural = _('Referenzwerte')

        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['window', 'name'],
        #         name='unique_variable_per_window'
        #     )
        # ]


class AbstractVariableInList(AbstractBaseModel):
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

    class Meta:
        abstract = True
        ordering = ['index']


class AbstractVariableValue(AbstractBaseModel):
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
        abstract = True
        verbose_name = _('Wert')
        verbose_name_plural = _('Werte')


class AbstractVariableSchema(AbstractBaseModel):
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
        abstract = True
        verbose_name = _('Vorlage')
        verbose_name_plural = _('Vorlagen')


class AbstractVariableSchemaField(AbstractBaseModel):
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

            instance: AbstractVariable
            for instance in self.schema.instances.filter(type=VariableType.DICT):
                instance.add_value(self)
        else:
            super().save(force_insert, force_update, using, update_fields)

            value: AbstractVariableValue
            for value in self.uses.all():
                value.name = self.name
                value.save()

    class Meta:
        abstract = True
        verbose_name = _('Feld')
        verbose_name_plural = _('Felder')
