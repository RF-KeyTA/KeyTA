from django.db import models
from django.utils.translation import gettext_lazy as _

from keyta.apps.keywords.models import KeywordCallParameterSource
from keyta.models.base_model import AbstractBaseModel


class VariableValue(AbstractBaseModel):
    variable = models.ForeignKey(
        'variables.Variable',
        on_delete=models.CASCADE,
        related_name='values'
    )
    index = models.PositiveSmallIntegerField(default=0)
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
        if self.name:
            return self.name
        else:
            return self.value

    @property
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
        ordering = ['index']
        verbose_name = _('Wert')
        verbose_name_plural = _('Werte')
