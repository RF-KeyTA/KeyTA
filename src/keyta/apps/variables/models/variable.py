from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from keyta.models.base_model import AbstractBaseModel


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
    setup_teardown = models.BooleanField(
        default=False,
        verbose_name=_('Vor-/Nachbereitung')
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

    def delete(self, using=None, keep_parents=False):
        super().delete(using, keep_parents)

        if self.table:
            self.table.reindex_columns()

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

    def reindex_columns(self):
        for index, column in enumerate(self.columns.all(), start=1):
            column.index = index
            column.save()

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
