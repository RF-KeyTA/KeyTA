import re
from typing import Optional

from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _

from model_clone import CloneMixin

from keyta.select_value import SelectValue
from .keywordcall_parameter_source import (
    KeywordCallParameterSource,
    KeywordCallParameterSourceType
)
from .keyword_parameters import KeywordParameterType


class KeywordCallParameter(CloneMixin, models.Model):
    keyword_call = models.ForeignKey(
        'keywords.KeywordCall',
        on_delete=models.CASCADE,
        related_name='parameters'
    )
    parameter = models.ForeignKey(
        'keywords.KeywordParameter',
        on_delete=models.CASCADE,
        related_name='uses'
    )
    value = models.CharField(
        max_length=255,
        verbose_name=_('Wert')
    )
    value_ref = models.ForeignKey(
        'keywords.KeywordCallParameterSource',
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True
    )

    class QuerySet(models.QuerySet):
        def args(self):
            return self.filter(parameter__type=KeywordParameterType.ARG)

        def kwargs(self):
            return self.filter(parameter__type=KeywordParameterType.KWARG)

    objects = QuerySet.as_manager()

    def __str__(self):
        return self.name

    @property
    def current_value(self) -> Optional[str]:
        if value_ref := self.value_ref:
            return str(value_ref)

        select_value = SelectValue.from_json(self.value)
        return select_value.user_input

    def make_clone(self, attrs=None, sub_clone=False, using=None, parent=None):
        clone: KeywordCallParameter = super().make_clone(attrs=attrs, sub_clone=sub_clone, using=using, parent=parent)
        select_value = SelectValue.from_json(clone.value)

        if value_ref := clone.value_ref:
            keyword = clone.keyword_call.from_keyword

            if value_ref.type == KeywordCallParameterSourceType.KEYWORD_PARAMETER:
                select_value.pk = KeywordCallParameterSource.objects.get(
                    kw_param=keyword.parameters.get(name=select_value.arg_name)
                ).pk

            if value_ref.type == KeywordCallParameterSourceType.KW_CALL_RETURN_VALUE:
                if keyword:
                    select_value.pk = KeywordCallParameterSource.objects.get(
                        kw_call_ret_val=keyword.calls.get(index=select_value.kw_call_index).return_value.first()
                    ).pk

                if testcase := clone.keyword_call.testcase:
                    select_value.pk = KeywordCallParameterSource.objects.get(
                        kw_call_ret_val=testcase.steps.get(index=select_value.kw_call_index).return_value.first()
                    ).pk

            clone.value = select_value.jsonify()
            clone.save()

        return clone

    @property
    def name(self):
        return self.parameter.name

    def save(
        self, force_insert=False, force_update=False, using=None,
        update_fields=None
    ):
        select_value = SelectValue.from_json(self.value)

        if pk := select_value.pk:
            self.value_ref = KeywordCallParameterSource.objects.get(id=pk)
        else:
            self.value_ref = None

        self.value = re.sub(r"\s{2,}", " ", self.value)
        super().save(force_insert, force_update, using, update_fields)

    def to_robot(self):
        if value_ref := self.value_ref:
            if value_ref.type == KeywordCallParameterSourceType.VARIABLE_VALUE:
                return value_ref.variable_value.value
            else:
                return '${' + str(self.value_ref) + '}'

        return self.current_value

    class Meta:
        verbose_name = _('Parameter')
        verbose_name_plural = _('Parameters')
