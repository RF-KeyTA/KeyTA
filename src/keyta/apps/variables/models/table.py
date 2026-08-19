from collections import defaultdict

from django.db.models import F, QuerySet
from django.utils.translation import gettext_lazy as _

from .variable import Variable
from .variable_value import VariableValue


class Table(Variable):
    def get_column_titles(self):
        return list(self.columns.order_by('index').values_list('name', flat=True))

    def get_row_variables(self, columns: list['Variable']):
        table = self.get_rows(columns)

        return {
            '@{%s__%s}' % (self.name, index): [col or '${EMPTY}' for col in row]
            for index, row in enumerate(table, start=1)
        }

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

    def to_robot(self):
        row_variables = self.get_row_variables(self.columns.all())
        table_variable = ('@{%s}' % self.name, list(row_variables.keys()))
        return table_variable, list(row_variables.items())

    class Meta:
        proxy = True
        verbose_name = _('Tabelle')
        verbose_name_plural = _('Tabellen')
