from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from model_clone import CloneMixin

from ..keywordcall_parameter_json_value import JSONValue
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
    # JSON representation of keyta.select_value.SelectValue
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
    # The parameters of ExecutionKeywordCall, Setup and Teardown are user-dependent
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
    def current_value(self):
        json_value = self.json_value
        
        if user_input := json_value.user_input:
            return user_input
    
        if pk := json_value.pk:
            return str(KeywordCallParameterSource.objects.get(pk=pk))

    def is_empty(self):
        return (
            not self.value_ref and 
            JSONValue.from_json(self.value).user_input in {None, ''}
        )

    @property
    def json_value(self) -> JSONValue:
        return JSONValue.from_json(self.value)

    def make_clone(self, attrs=None, sub_clone=False, using=None, parent=None):
        clone: KeywordCallParameter = super().make_clone(attrs=attrs, sub_clone=sub_clone, using=using, parent=parent)
        select_value = JSONValue.from_json(clone.value)

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

    def reset_value(self):
        self.value = JSONValue(None, None, None, None).jsonify()

    def save(
        self, force_insert=False, force_update=False, using=None,
        update_fields=None
    ):
        json_value = JSONValue.from_json(self.value)

        if pk := json_value.pk:
            self.value_ref = KeywordCallParameterSource.objects.get(id=pk)
        else:
            self.value_ref = None

        super().save(force_insert, force_update, using, update_fields)

    def to_robot(self):
        if value_ref := self.value_ref:
            return value_ref.to_robot()
        else:
            return JSONValue.from_json(self.value).user_input

    def update_value(self):
        if self.value_ref:
            self.value = self.value_ref.get_value().jsonify()
            self.save()

    class Meta:
        ordering = ['parameter__position']
        verbose_name = _('Parameter')
        verbose_name_plural = _('Parameters')
