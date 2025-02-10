from django.db import models
from django.utils.translation import gettext as _

from model_clone import CloneMixin

from keyta.select_value import SelectValue
from .keywordcall_parameter_source import (
    KeywordCallParameterSource,
    KeywordCallParameterSourceType
)


class KeywordCallReturnValue(CloneMixin, models.Model):
    keyword_call = models.ForeignKey(
        'keywords.KeywordCall',
        on_delete=models.CASCADE,
        related_name='return_value'
    )
    return_value = models.ForeignKey(
        'keywords.KeywordCallReturnValue',
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

        if self.return_value:
            return str(self.return_value)

        return _('Kein Rückgabewert')

    @property
    def is_set(self):
        return self.name or self.return_value

    def jsonify(self):
        return SelectValue(
            arg_name=None,
            kw_call_index=self.keyword_call.index,
            pk=self.return_value.pk,
            user_input=None
        ).jsonify()

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
