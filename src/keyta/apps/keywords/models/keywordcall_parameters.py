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


class RobotVariable(models.TextChoices):
    DICTIONARY_ITEM = 'DICTIONARY_ITEM', _('dict.item -> ${dict}[item]')


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
    robot_variable = models.CharField(
        max_length=255,
        choices=RobotVariable.choices,
        blank=True,
        verbose_name=_('Format (optional)')
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
        clone_value = JSONValue.from_json(clone.value)

        if value_ref := clone.value_ref:
            clone_keyword = clone.keyword_call.from_keyword

            if value_ref.type == KeywordCallParameterSourceType.KEYWORD_PARAMETER:
                clone_value.pk = KeywordCallParameterSource.objects.get(
                    kw_param=clone_keyword.parameters.get(name=clone_value.arg_name)
                ).pk

            if value_ref.type == KeywordCallParameterSourceType.KW_CALL_RETURN_VALUE:
                if clone_keyword:
                    clone_kwcall = clone_keyword.calls.get(index=clone_value.kw_call_index)
                    clone_kw_call_return_values = {
                        str(kw_call_return_value): kw_call_return_value
                        for kw_call_return_value in clone_kwcall.return_values.all()
                    }
                    clone_value.pk = KeywordCallParameterSource.objects.get(
                        kw_call_ret_val=clone_kw_call_return_values[str(self.value_ref.kw_call_ret_val)]
                    ).pk

                if testcase := clone.keyword_call.testcase:
                    clone_test_step = testcase.steps.get(index=clone_value.kw_call_index)
                    clone_test_step_return_values = {
                        str(test_step_return_value): test_step_return_value
                        for test_step_return_value in clone_test_step.return_values.all()
                    }
                    clone_value.pk = KeywordCallParameterSource.objects.get(
                        kw_call_ret_val=clone_test_step_return_values[str(self.value_ref.kw_call_ret_val)]
                    ).pk

            clone.value = clone_value.jsonify()
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

    def to_robot(self, get_variable_value):
        if value_ref := self.value_ref:
            return value_ref.to_robot(get_variable_value)
        else:
            user_input = JSONValue.from_json(self.value).user_input

            if self.robot_variable == RobotVariable.DICTIONARY_ITEM:
                dict_, item = user_input.split('.')
                return '${%s}[%s]' % (dict_, item)

            return user_input

    def update_value(self):
        if self.value_ref:
            self.value = self.value_ref.get_value().jsonify()
            self.save()

    class Meta:
        ordering = ['parameter__position']
        verbose_name = _('Parameter')
        verbose_name_plural = _('Parameters')
