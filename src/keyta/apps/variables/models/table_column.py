from django.utils.translation import gettext_lazy as _

from keyta.apps.keywords.models import KeywordCallParameterSource

from .variable import Variable, VariableType


class TableColumn(Variable):
    def save(
        self, force_insert=False, force_update=False, using=None,
            update_fields=None
    ):
        self.type = VariableType.LIST

        if not self.pk:
            super().save(force_insert, force_update, using, update_fields)
            KeywordCallParameterSource.objects.create(table_column=self)
        else:
            super().save(force_insert, force_update, using, update_fields)

    class Meta:
        proxy = True
        verbose_name = _('Spalte')
        verbose_name_plural = _('Spalten')
