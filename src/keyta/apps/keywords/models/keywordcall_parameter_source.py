from django.db import models
from django.db.models import Q


class KeywordCallParameterSourceType(models.TextChoices):
    KEYWORD_PARAMETER = 'KEYWORD_PARAMETER', 'Schlüsselwort-Parameter'
    KW_CALL_RETURN_VALUE = 'KW_CALL_RETURN_VALUE', 'Aufrufs-Rückgabewert'
    VARIABLE_VALUE = 'VARIABLE_VALUE', 'Referenzwert'


class KeywordCallParameterSource(models.Model):
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

    def __str__(self):
        return str(
            self.kw_param or
            self.kw_call_ret_val or
            self.variable_value
        )

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
        verbose_name = 'Parameter-Referenz'
        verbose_name_plural = 'Parameter-Referenzen'
