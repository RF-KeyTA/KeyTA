from django.db import models
from django.utils.translation import gettext_lazy as _

from model_clone import CloneMixin

from keyta.models.base_model import AbstractBaseModel

from .keyword import KeywordType


class KeywordReturnValue(CloneMixin, AbstractBaseModel):
    keyword = models.ForeignKey(
        'keywords.Keyword',
        on_delete=models.CASCADE,
        related_name='return_values'
    )
    kw_call_return_value = models.ForeignKey(
        'keywords.KeywordCallReturnValue',
        null=True,
        default=None,
        on_delete=models.CASCADE,
        verbose_name=_('Rückgabewert')
    )
    kw_call_index = models.PositiveSmallIntegerField(
        default=0
    )
    typedoc = models.CharField(
        max_length=255,
        blank=True
    )

    def __str__(self):
        if self.kw_call_return_value:
            return str(self.kw_call_return_value)

        return ''

    def delete(self, using=None, keep_parents=False):
        # Exclude keyword execution calls
        for kw_call in self.keyword.uses.all().exclude(execution__isnull=False):
            kw_call.delete_return_value(self)

        super().delete(using, keep_parents)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.kw_call_return_value:
            self.kw_call_index = self.kw_call_return_value.keyword_call.index

        if not self.pk:
            super().save(force_insert, force_update, using, update_fields)

            if not self.keyword.type in {KeywordType.LIBRARY, KeywordType.RESOURCE}:
                # Exclude keyword execution calls
                for kw_call in self.keyword.uses.all().exclude(execution__isnull=False):
                    kw_call.add_return_value(self)
        else:
            super().save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = _('Rückgabewert')
        verbose_name_plural = _('Rückgabewert')
