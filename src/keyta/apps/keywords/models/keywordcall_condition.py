from django.db import models
from django.utils.translation import gettext_lazy as _


class OperatorChoices(models.TextChoices):
    IS_EQUAL = 'IS_EQUAL', _('Gleich')
    NOT_EQUAL = 'NOT_EQUAL', _('Ungleich')
    NOT_EMPTY = 'NOT_EMPTY', _('Nicht leer')


class KeywordCallCondition(models.Model):
    left_operand = models.CharField(
        max_length=255,
        verbose_name=_('Erster Parameter')
    )
    operator = models.CharField(
        choices=OperatorChoices.choices,
        max_length=255,
        verbose_name=_('Operator')
    )
    right_operand = models.CharField(
        max_length=255,
        verbose_name=_('Zweiter Parameter')
    )
    keyword_call = models.ForeignKey(
        'keywords.KeywordCall',
        on_delete=models.CASCADE,
        related_name='conditions'
    )

    def __str__(self):
        return self.value

    class Meta:
        verbose_name=_('Bedingung')
        verbose_name_plural=_('Bedingungen')
