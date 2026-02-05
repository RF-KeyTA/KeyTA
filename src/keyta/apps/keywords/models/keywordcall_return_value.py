from django.db import models
from django.utils.translation import gettext, gettext_lazy as _

from model_clone import CloneMixin

from keyta.models.base_model import AbstractBaseModel

from .keywordcall_parameter_source import (
    KeywordCallParameterSource,
    KeywordCallParameterSourceType
)


class KeywordCallReturnValue(CloneMixin, AbstractBaseModel):
    keyword_call = models.ForeignKey(
        'keywords.KeywordCall',
        on_delete=models.CASCADE,
        related_name='return_values'
    )
    kw_call_return_value = models.ForeignKey(
        'keywords.KeywordCallReturnValue',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    return_value = models.ForeignKey(
        'keywords.KeywordReturnValue',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default=None
    )

    def __str__(self):
        if self.name:
            return self.name

        if self.kw_call_return_value:
            return str(self.kw_call_return_value)

        return gettext('Kein Rückgabewert')

    @property
    def is_set(self):
        return self.name or self.kw_call_return_value

    @property
    def type(self):
        if self.return_value:
            return self.return_value.type

        if self.kw_call_return_value:
            return self.kw_call_return_value.type

    @property
    def typedoc(self):
        if self.return_value:
            return self.return_value.get_typedoc()

        if self.kw_call_return_value:
            return self.kw_call_return_value.typedoc

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.pk:
            super().save(force_insert, force_update, using, update_fields)

            KeywordCallParameterSource.objects.create(
                kw_call_ret_val=self,
                type=KeywordCallParameterSourceType.KW_CALL_RETURN_VALUE
            )
        else:
            super().save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = _('Rückgabewert')
        verbose_name_plural = _('Rückgabewerte')
