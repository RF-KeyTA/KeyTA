from django.db import models
from django.utils.translation import gettext as _

from keyta.models.base_model import AbstractBaseModel


class KeywordReturnValue(AbstractBaseModel):
    keyword = models.ForeignKey(
        'keywords.Keyword',
        on_delete=models.CASCADE,
        related_name='return_value'
    )
    kw_call_return_value = models.ForeignKey(
        'keywords.KeywordCallReturnValue',
        on_delete=models.CASCADE,
        verbose_name=_('Rückgabewert')
    )

    def __str__(self):
        if self.kw_call_return_value:
            return str(self.kw_call_return_value)

        return ''

    class Meta:
        verbose_name = _('Rückgabewert')
        verbose_name_plural = _('Rückgabewert')
