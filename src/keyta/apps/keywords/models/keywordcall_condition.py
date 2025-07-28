from django.db import models
from django.utils.translation import gettext_lazy as _

from keyta.models.base_model import AbstractBaseModel


class ConditionChoices(models.TextChoices):
    CONTAINS = 'in', _('ist Teil von')
    IS_EQUAL = '==', _('ist')
    NOT_EQUAL = '!=', _('ist nicht')


class KeywordCallCondition(AbstractBaseModel):
    keyword_parameter = models.ForeignKey(
        'keywords.KeywordParameter',
        on_delete=models.CASCADE,
        verbose_name=_('Parameter'),
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
        return '"${' + str(self.keyword_parameter) + '}"' + f' {self.condition} "{self.expected_value}"'

    class Meta:
        verbose_name=_('Bedingung')
        verbose_name_plural=_('Bedingungen')
