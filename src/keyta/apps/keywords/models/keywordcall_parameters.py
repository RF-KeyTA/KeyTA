import json
import re
from typing import Optional

from django.db import models

from django.contrib.auth.models import User

from .keywordcall_parameter_source import (
    KeywordCallParameterSource,
    KeywordCallParameterSourceType
)
from .keyword_parameters import KeywordParameterType


def jsonify(value: Optional[str], pk: Optional[int]):
    return json.dumps({
        "value": value,
        "pk": pk
    })


class KeywordCallParameter(models.Model):
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
        verbose_name='Wert'
    )
    value_ref = models.ForeignKey(
        KeywordCallParameterSource,
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )
    user = models.ForeignKey(
        User,
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

        value_pk = json.loads(self.value)
        return value_pk['value']

    @property
    def name(self):
        return self.parameter.name

    def save(
        self, force_insert=False, force_update=False, using=None,
        update_fields=None
    ):
        value_pk = json.loads(self.value)
        if pk := value_pk['pk']:
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
                return '${' + self.current_value + '}'

        return self.current_value

    class Meta:
        verbose_name = 'Aufrufparameter'
        verbose_name_plural = 'Aufrufparameter'
