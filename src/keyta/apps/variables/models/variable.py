from django.db import models

from apps.common.abc import AbstractBaseModel
from apps.keywords.models import (
    KeywordCallParameterSource,
    KeywordCallParameterSourceType
)


class Variable(AbstractBaseModel):
    name = models.CharField(max_length=255, verbose_name='Name')

    # Customization #
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Beschreibung'
    )
    setup_teardown = models.BooleanField(
        default=False,
        verbose_name='Vor-/Nachbereitung'
    )
    all_windows = models.BooleanField(
        default=False,
        verbose_name='In allen Masken'
    )
    systems = models.ManyToManyField(
        'systems.System',
        blank=True,
        related_name='variables',
        verbose_name='Systeme'
    )
    windows = models.ManyToManyField(
        'windows.Window',
        related_name='variables',
        verbose_name='Masken'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Referenzwert'
        verbose_name_plural = 'Referenzwerte'

        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['window', 'name'],
        #         name='unique_variable_per_window'
        #     )
        # ]


class VariableValue(AbstractBaseModel):
    variable = models.ForeignKey(Variable, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name='Name')
    value = models.CharField(max_length=255, verbose_name='Wert')

    def __str__(self):
        return f'{self.variable.name}: {self.name}'

    def save(
        self, force_insert=False, force_update=False, using=None,
            update_fields=None
    ):

        if not self.pk:
            super().save(force_insert, force_update, using, update_fields)

            KeywordCallParameterSource.objects.create(
                variable_value=self,
                type=KeywordCallParameterSourceType.VARIABLE_VALUE
            )
        else:
            super().save(force_insert, force_update, using, update_fields)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['variable', 'name'],
                name='unique_value_per_variable'
            )
        ]
        verbose_name = 'Wert'
        verbose_name_plural = 'Werte'
