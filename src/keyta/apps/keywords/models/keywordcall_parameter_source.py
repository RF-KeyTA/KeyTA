from django.db import models
from django.db.models import Q
from django.utils.translation import gettext as _

from model_clone import CloneMixin

from keyta.select_value import SelectValue


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

    def jsonify(self):
        if self.kw_param:
            return SelectValue(
                arg_name=self.kw_param.name,
                kw_call_index=None,
                pk=self.pk,
                user_input=None
            ).jsonify()

        if self.kw_call_ret_val:
            return SelectValue(
                arg_name=None,
                kw_call_index=self.kw_call_ret_val.keyword_call.index,
                pk=self.pk,
                user_input=None
            ).jsonify()

        return SelectValue(
            arg_name=None,
            kw_call_index=None,
            pk=self.pk,
            user_input=None
        ).jsonify()

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
