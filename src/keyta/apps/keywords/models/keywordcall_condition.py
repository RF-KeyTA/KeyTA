from django.db import models
from django.utils.translation import gettext_lazy as _

from model_clone import CloneMixin

from keyta.models.base_model import AbstractBaseModel

from ..json_value import JSONValue
from .keywordcall_parameter_source import KeywordCallParameterSource


class ConditionChoices(models.TextChoices):
    CONTAINS = 'in', _('enthält')
    NOT_CONTAINS = 'not in', _('enthält nicht')
    IS_EQUAL = '==', _('ist')
    NOT_EQUAL = '!=', _('ist nicht')


class KeywordCallCondition(CloneMixin, AbstractBaseModel):
    value_ref = models.ForeignKey(
        'keywords.KeywordCallParameterSource',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Wert'),
    )
    condition = models.CharField(
        choices=ConditionChoices.choices,
        max_length=255,
        verbose_name=_('Bedingung'),
    )
    # JSON representation of keyta.apps.keywords.json_value.JSONValue
    expected_value = models.CharField(
        max_length=255,
        verbose_name=_('Soll Wert')
    )
    expected_value_ref = models.ForeignKey(
        'keywords.KeywordCallParameterSource',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expected_values'
    )
    keyword_call = models.ForeignKey(
        'keywords.KeywordCall',
        on_delete=models.CASCADE,
        related_name='conditions'
    )

    def __str__(self):
        if self.expected_value:
            expected_value = JSONValue.from_json(self.expected_value)
            user_input = expected_value.user_input

            if user_input is not None:
                exp_value = user_input
            else:
                exp_value = '${' +  str(self.expected_value_ref) + '}'

            if self.condition in {ConditionChoices.IS_EQUAL, ConditionChoices.NOT_EQUAL}:
                return '"${' + str(self.value_ref) + '}"' + f' {self.condition} "{exp_value}"'

            if self.condition in {ConditionChoices.CONTAINS, ConditionChoices.NOT_CONTAINS}:
                return f'"{exp_value}" {self.condition} ' + '"${' + str(self.value_ref) + '}"'

        return super().__str__()

    def save(
        self, force_insert=False, force_update=False, using=None,
        update_fields=None
    ):
        json_value = JSONValue.from_json(self.expected_value)

        if pk := json_value.pk:
            self.expected_value_ref = KeywordCallParameterSource.objects.get(id=pk)
        else:
            self.expected_value_ref = None

        super().save(force_insert, force_update, using, update_fields)

    def update_expected_value(self):
        if self.expected_value_ref:
            self.expected_value = self.expected_value_ref.get_value().jsonify()
            self.save()

    class Meta:
        verbose_name=_('Vorbedingung')
        verbose_name_plural=_('Vorbedingungen')
