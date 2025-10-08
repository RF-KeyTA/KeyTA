from collections import defaultdict

from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from keyta.models.base_model import AbstractBaseModel

from .variable_value import VariableValue


class VariableType(models.TextChoices):
    DICT = 'DICT', _('Formular')
    LIST = 'LIST', _('Werteliste')
    TABLE = 'TABLE', _('Tabelle')


class Variable(AbstractBaseModel):
    name = models.CharField(max_length=255, verbose_name=_('Name'))

    # Customization #
    systems = models.ManyToManyField(
        'systems.System',
        related_name='variables',
        verbose_name=_('Systeme')
    )
    table = models.ForeignKey(
        'variables.Variable',
        default=None,
        null=True,
        on_delete=models.CASCADE,
        related_name='columns',
        verbose_name=_('Tabelle')
    )
    windows = models.ManyToManyField(
        'windows.Window',
        related_name='variables',
        verbose_name=_('Masken')
    )

    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Beschreibung')
    )
    index = models.PositiveSmallIntegerField(
        default=0
    )
    template = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Vorlage')
    )
    type = models.CharField(
        max_length=255,
        choices=sorted(VariableType.choices, key=lambda kv: kv[1]),
        default=VariableType.DICT,
        verbose_name=_('Art')
    )

    def __str__(self):
        return self.name

    def get_rows(self):
        def row_variable(index):
            return '@{%s__%s}' % (self.name, index)

        table_values = (
            VariableValue.objects
            .filter(variable__in=self.columns.all())
            .values_list('index', 'variable__index', 'value')
        )
        row_variables = defaultdict(lambda: ['${EMPTY}']*self.columns.count())

        for row_index, col_index, value in table_values:
            row_variables[row_variable(row_index)][col_index-1] = value

        table_variable = ('@{%s}' % self.name, list(row_variables.keys()))

        return table_variable, list(row_variables.items())

    def is_dict(self):
        return self.type == VariableType.DICT

    def is_list(self):
        return self.type == VariableType.LIST

    def is_table(self):
        return self.type == VariableType.TABLE

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.table:
            self.systems.set(self.table.systems.all())
            self.windows.set(self.table.windows.all())

            super().save(*args, **kwargs)

    def to_robot(self, get_variable_value):
        if self.is_dict():
            return (
                '&{%s}' % self.name,
                {
                    value.name: get_variable_value(value.pk)
                    for value in self.values.all()
                }
            )

        if self.is_list():
            return (
                '@{%s}' % self.name,
                [
                    get_variable_value(value.pk)
                    for value in self.values.all()
                ]
            )

    class Meta:
        ordering = ['index', Lower('name')]
        verbose_name = _('Referenzwert')
        verbose_name_plural = _('Referenzwerte')


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
