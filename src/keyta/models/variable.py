from django.db import models
from django.utils.translation import gettext as _

from keyta.apps.keywords.models import KeywordCallParameterSource

from .base_model import AbstractBaseModel


class VariableType(models.TextChoices):
    DICT = 'DICT', _('Name-Wert Paaren')
    LIST = 'LIST', _('Tabelle')


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
        on_delete=models.CASCADE
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
        verbose_name=_('Datenstruktur')
    )
    windows = models.ManyToManyField(
        'windows.Window',
        related_name='variables',
        verbose_name=_('Masken')
    )

    def __str__(self):
        return self.name

    def is_dict(self):
        return self.type == VariableType.DICT

    def is_list(self):
        return self.type == VariableType.LIST

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
    list_variable = models.ForeignKey(
        'variables.Variable',
        on_delete=models.CASCADE,
        related_name='elements'
    )
    variable = models.ForeignKey(
        'variables.Variable',
        on_delete=models.CASCADE,
        related_name='in_list'
    )
    index = models.PositiveSmallIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ['index']


class AbstractVariableValue(AbstractBaseModel):
    variable = models.ForeignKey(
        'variables.Variable',
        on_delete=models.CASCADE
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
        constraints = [
            models.UniqueConstraint(
                fields=['variable', 'name'],
                name='unique_value_per_variable'
            )
        ]
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
        verbose_name = _('Schema')
        verbose_name_plural = _('Schemas')


class AbstractVariableSchemaField(AbstractBaseModel):
    schema = models.ForeignKey(
        'variables.VariableSchema',
        on_delete=models.CASCADE,
        related_name='fields'
    )
    name = models.CharField(
        max_length=255
    )

    class Meta:
        abstract = True
        verbose_name = _('Field')
        verbose_name_plural = _('Fields')
