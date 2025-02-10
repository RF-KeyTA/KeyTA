from django.db import models
from django.utils.translation import gettext as _

from model_clone import CloneMixin

from keyta.models.base_model import AbstractBaseModel


class KeywordReturnValue(CloneMixin, AbstractBaseModel):
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
    kw_call_index = models.PositiveSmallIntegerField()

    def __str__(self):
        if self.kw_call_return_value:
            return str(self.kw_call_return_value)

        return ''

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.kw_call_index = self.kw_call_return_value.keyword_call.index
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = _('Rückgabewert')
        verbose_name_plural = _('Rückgabewert')
