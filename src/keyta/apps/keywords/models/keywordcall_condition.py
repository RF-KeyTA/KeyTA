from django.db import models
from django.utils.translation import gettext_lazy as _

from keyta.models.base_model import AbstractBaseModel


class ConditionChoices(models.TextChoices):
    CONTAINS = 'in', _('enthält')
    IS_EQUAL = '==', _('ist')
    NOT_EQUAL = '!=', _('ist nicht')


class KeywordCallCondition(AbstractBaseModel):
    value_ref = models.ForeignKey(
        'keywords.KeywordCallParameterSource',
        on_delete=models.PROTECT,
        verbose_name=_('Wert'),
    )
    condition = models.CharField(
        choices=ConditionChoices.choices,
        max_length=255,
        verbose_name=_('Bedingung'),
    )
    expected_value = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Soll Wert')
    )
    keyword_call = models.ForeignKey(
        'keywords.KeywordCall',
        on_delete=models.CASCADE,
        related_name='conditions'
    )

    def __str__(self):
        if self.condition in {ConditionChoices.IS_EQUAL, ConditionChoices.NOT_EQUAL}:
            return '"${' + str(self.value_ref) + '}"' + f' {self.condition} "{self.expected_value}"'

        if self.condition == ConditionChoices.CONTAINS:
            return f'"{self.expected_value}" {self.condition} ' + '"${' + str(self.value_ref) + '}"'


    class Meta:
        verbose_name=_('Bedingung')
        verbose_name_plural=_('Bedingungen')
