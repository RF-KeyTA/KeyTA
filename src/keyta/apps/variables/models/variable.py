from django.db import models
from django.utils.translation import gettext as _

from keyta.models.base_model import AbstractBaseModel

from apps.keywords.models import (
    KeywordCallParameterSource,
    KeywordCallParameterSourceType
)


class Variable(AbstractBaseModel):
    name = models.CharField(max_length=255, verbose_name=_('Name'))

    # Customization #
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Beschreibung')
    )
    systems = models.ManyToManyField(
        'systems.System',
        related_name='variables',
        verbose_name=_('Systeme')
    )
    windows = models.ManyToManyField(
        'windows.Window',
        related_name='variables',
        verbose_name=_('Masken')
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Referenzwert')
        verbose_name_plural = _('Referenzwerte')

        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['window', 'name'],
        #         name='unique_variable_per_window'
        #     )
        # ]


class VariableValue(AbstractBaseModel):
    variable = models.ForeignKey(Variable, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    value = models.CharField(max_length=255, verbose_name=_('Wert'))

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
        verbose_name = _('Wert')
        verbose_name_plural = _('Werte')


class VariableWindow(AbstractBaseModel, Variable.windows.through):
    def __str__(self):
        return str(self.window)

    class Meta:
        auto_created = True
        proxy = True
        verbose_name = _('Beziehung zu Maske')
        verbose_name_plural = _('Beziehungen zu Masken')


class WindowVariable(Variable):
    def __str__(self):
        return str(self.name)

    class Meta:
        proxy = True
        verbose_name = _('Referenzwert')
        verbose_name_plural = _('Referenzwerte')
