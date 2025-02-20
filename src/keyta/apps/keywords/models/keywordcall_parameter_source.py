from django.db import models
from django.db.models import Q
from django.utils.translation import gettext as _

from model_clone import CloneMixin

from ..keywordcall_parameter_json_value import JSONValue


class KeywordCallParameterSourceType(models.TextChoices):
    KEYWORD_PARAMETER = 'KEYWORD_PARAMETER', _('Schlüsselwort-Parameter')
    KW_CALL_RETURN_VALUE = 'KW_CALL_RETURN_VALUE', _('Aufrufs-Rückgabewert')
    VARIABLE_VALUE = 'VARIABLE_VALUE', _('Referenzwert')


class KeywordCallParameterSource(CloneMixin, models.Model):
    kw_param = models.OneToOneField(
        'keywords.KeywordParameter',
        on_delete=models.CASCADE,
        null=True,
        default=None
    )
    kw_call_ret_val = models.OneToOneField(
        'keywords.KeywordCallReturnValue',
        on_delete=models.CASCADE,
        null=True,
        default=None
    )
    variable_value = models.OneToOneField(
        'variables.VariableValue',
        on_delete=models.CASCADE,
        null=True,
        default=None
    )
    type = models.CharField(
        max_length=255,
        choices=KeywordCallParameterSourceType.choices
    )

    _clone_o2o_fields = ['kw_param', 'kw_call_ret_val', 'variable_value']

    def __str__(self):
        return str(
            self.kw_param or
            self.kw_call_ret_val or
            self.variable_value
        )

    def get_value(self) -> JSONValue:
        if self.kw_param:
            return JSONValue(
                arg_name=self.kw_param.name,
                kw_call_index=None,
                pk=self.pk,
                user_input=None
            )

        if self.kw_call_ret_val:
            return JSONValue(
                arg_name=None,
                kw_call_index=self.kw_call_ret_val.keyword_call.index,
                pk=self.pk,
                user_input=None
            )

        if self.variable_value:
            return JSONValue(
                arg_name=None,
                kw_call_index=None,
                pk=self.pk,
                user_input=None
            )

    def save(self, force_insert=False, force_update=False, using=None,
        update_fields=None):

        if self.kw_param:
            self.type = KeywordCallParameterSourceType.KEYWORD_PARAMETER

        if self.kw_call_ret_val:
            self.type = KeywordCallParameterSourceType.KW_CALL_RETURN_VALUE

        if self.variable_value:
            self.type = KeywordCallParameterSourceType.VARIABLE_VALUE

        super().save(force_insert, force_update, using, update_fields)

    def to_robot(self):
        if self.type == KeywordCallParameterSourceType.VARIABLE_VALUE:
            return self.variable_value.value
        else:
            return '${' + str(self) + '}'

    class Meta:
        constraints = [
            models.CheckConstraint(
                name='kw_call_parameter_source_sum_type',
                check=
                (Q(type=KeywordCallParameterSourceType.KEYWORD_PARAMETER) &
                 Q(kw_param__isnull=False) &
                 Q(kw_call_ret_val__isnull=True) &
                 Q(variable_value__isnull=True))
                |
                (Q(type=KeywordCallParameterSourceType.KW_CALL_RETURN_VALUE) &
                 Q(kw_param__isnull=True) &
                 Q(kw_call_ret_val__isnull=False) &
                 Q(variable_value__isnull=True))
                |
                (Q(type=KeywordCallParameterSourceType.VARIABLE_VALUE) &
                 Q(kw_param__isnull=True) &
                 Q(kw_call_ret_val__isnull=True) &
                 Q(variable_value__isnull=False))
            )
        ]
        verbose_name = _('Parameter-Referenz')
        verbose_name_plural = _('Parameter-Referenzen')
