from django.db import models

from apps.common.abc import AbstractBaseModel
from .keyword import Keyword


class KeywordReturnValue(AbstractBaseModel):
    keyword = models.ForeignKey(
        Keyword,
        on_delete=models.CASCADE,
        related_name='return_value'
    )
    kw_call_return_value = models.ForeignKey(
        'keywords.KeywordCallReturnValue',
        on_delete=models.CASCADE,
        verbose_name='Rückgabewert'
    )

    def __str__(self):
        if self.kw_call_return_value:
            return str(self.kw_call_return_value)

        return ''

    class Meta:
        verbose_name = 'Rückgabewert'
        verbose_name_plural = 'Rückgabewert'
