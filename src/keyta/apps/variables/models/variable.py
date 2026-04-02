from collections import defaultdict

from django.db import models
from django.db.models import F, QuerySet
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from keyta.models.base_model import AbstractBaseModel

from .variable_value import VariableValue


def get_row_variables(table_name: str, table: list[list[str]]):
    return {
        row_variable(table_name, index): [col or '${EMPTY}' for col in row]
        for index, row in enumerate(table)
    }


def row_variable(name, index):
    return '@{%s__%s}' % (name, index)


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

    def get_column_titles(self):
        return [
            column.name
            for column in self.columns.all()
        ]

    def get_rows(self, columns: list['Variable']|QuerySet):
        cells = (
            VariableValue.objects
            .filter(variable__in=columns)
            .annotate(column_index=F('variable__index'))
            .annotate(row_index=F('index'))
            .order_by('row_index')
            .values_list('row_index', 'column_index', 'value')
        )
        column_order = {
            column.index: c
            for c, column in enumerate(columns)
        }
        table = defaultdict(lambda: ['']*len(columns))

        for row_index, column_index, value in cells:
            table[row_index][column_order[column_index]] = value

        return list(table.values())

    @property
    def is_column(self):
        return self.table is not None

    @property
    def is_dict(self):
        return self.type == VariableType.DICT

    @property
    def is_list(self):
        return self.type == VariableType.LIST

    @property
    def is_table(self):
        return self.type == VariableType.TABLE

    def reindex_column(self):
        for index, value in enumerate(self.values.all(), start=1):
            value.index = index
            value.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.table:
            self.systems.set(self.table.systems.all())
            self.windows.set(self.table.windows.all())

            super().save(*args, **kwargs)

    def to_robot(self):
        if self.is_dict:
            return (
                '&{%s}' % self.name,
                {
                    value.name: value.value
                    for value in self.values.all()
                }
            )

        if self.is_list:
            return (
                '@{%s}' % self.name,
                [
                    value.value
                    for value in self.values.all()
                ]
            )

        if self.is_table:
            table_row_variables = get_row_variables(self.name, self.get_rows(self.columns.all()))
            table_variable = ('@{%s}' % self.name, list(table_row_variables.keys()))
            return table_variable, list(table_row_variables.items())

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
