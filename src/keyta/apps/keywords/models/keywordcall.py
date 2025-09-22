from typing import Optional

from django.conf import settings
from django.db import models
from django.db.models import Q, QuerySet, UniqueConstraint
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from model_clone import CloneMixin

from keyta.models.base_model import AbstractBaseModel
from keyta.rf_export.keywords import RFKeywordCall
from keyta.widgets import Icon

from ..json_value import JSONValue
from .keywordcall_condition import KeywordCallCondition
from .keywordcall_parameters import KeywordCallParameter
from .keywordcall_return_value import KeywordCallReturnValue
from .keyword_parameters import KeywordParameter, KeywordParameterType
from .keyword_return_value import KeywordReturnValue


class TestSetupTeardown(models.TextChoices):
    TEST_SETUP = 'TEST_SETUP', _('Testvorbereitung')
    TEST_TEARDOWN = 'TEST_TEARDOWN', _('Testnachbereitung')


class SuiteSetupTeardown(models.TextChoices):
    SUITE_SETUP = 'SUITE_SETUP', _('Suitevorbereitung')
    SUITE_TEARDOWN = 'SUITE_TEARDOWN', _('Suitenachbereitung')


class KeywordCallType(models.TextChoices):
    KEYWORD_CALL = 'KEYWORD_CALL', _('Schlüsselwort-Aufruf')
    KEYWORD_EXECUTION = 'KEYWORD_EXECUTION', _('Schlüsselwort Ausführung')
    TEST_STEP = 'TEST_STEP', _('Testschritt')


class KeywordCall(CloneMixin, AbstractBaseModel):
    from_keyword = models.ForeignKey(
        'keywords.Keyword',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        blank=True,
        related_name='calls'
    )
    testcase = models.ForeignKey(
        'testcases.TestCase',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        blank=True,
        related_name='steps'
    )
    execution = models.ForeignKey(
        'executions.Execution',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        blank=True,
        related_name='keyword_calls'
    )
    to_keyword = models.ForeignKey(
        'keywords.Keyword',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='uses'
    )
    enabled = models.BooleanField(
        default=True,
        verbose_name=''
    )
    execute = models.BooleanField(
        default=False,
        verbose_name='▶'
    )
    index = models.PositiveSmallIntegerField(
        default=0,
        db_index=True
    )
    type = models.CharField(
        max_length=255,
        choices=KeywordCallType.choices +
        TestSetupTeardown.choices +
        SuiteSetupTeardown.choices
    )

    # --Customization--
    # In a TestCase a keyword call may use values from the selected Variable
    variable = models.ForeignKey(
        'variables.Variable',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        blank=True,
        verbose_name=_('Referenzwert (optional)')
    )
    # In a TestCase keyword calls depend on the selected Window
    window = models.ForeignKey(
        'windows.Window',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        blank=True,
        verbose_name=_('Maske')
    )

    _clone_m2o_or_o2m_fields = ['conditions', 'parameters', 'return_values']

    def __repr__(self):
        return super().__repr__().replace('KeywordCall', f'KeywordCall({self.type})')

    def __str__(self):
        return f'{self.caller} → {self.to_keyword}'

    def add_parameter(
        self,
        param: KeywordParameter,
        user: Optional[AbstractUser]=None
    ):
        KeywordCallParameter.objects.get_or_create(
            keyword_call=self,
            parameter=param,
            user=user,
            defaults={
                'value': JSONValue(
                    arg_name=None,
                    kw_call_index=None,
                    pk=None,
                    user_input=param.default_value
                ).jsonify()
            }
        )

    def add_return_value(self, return_value: KeywordReturnValue):
        if return_value.type:
            KeywordCallReturnValue.objects.get_or_create(
                keyword_call=self,
                kw_call_return_value=return_value.kw_call_return_value,
                name=_('Rückgabewert'),
                return_value=return_value
            )
        else:
            KeywordCallReturnValue.objects.get_or_create(
                keyword_call=self,
                kw_call_return_value=return_value.kw_call_return_value
            )

    def delete_conditions(self):
        condition: KeywordCallCondition
        for condition in self.conditions.all():
            condition.delete()

    def delete_parameters(self):
        param: KeywordCallParameter
        for param in self.parameters.all():
            param.delete()

    def delete_return_value(self, return_value: KeywordReturnValue):
        self.return_values.get(kw_call_return_value__id=return_value.kw_call_return_value.pk).delete()

    def delete_return_values(self):
        return_value: KeywordReturnValue
        for return_value in self.return_values.all():
            return_value.delete()

    def delete_variable(self):
        self.variable = None
        self.save()

    @property
    def caller(self):
        if self.pk:
            return self.from_keyword or self.testcase or self.execution
        return None

    def get_icon(self, user: Optional[AbstractUser] = None) -> Icon|None:
        to_keyword_parameters_count = self.to_keyword.parameters.count()
        has_return_values = self.return_values.exists()

        if not self.pk or not self.to_keyword:
            return None

        if to_keyword_parameters_count == 0:
            if not has_return_values:
                if not (self.to_keyword.library or self.to_keyword.resource):
                    icon = Icon(
                        settings.FA_ICONS.kw_call_no_input_no_output,
                        {
                            'color': 'black',
                            'font-size': '18px',
                            'margin-left': '12px',
                            'margin-top': '8px'
                        }
                    )
                    icon.attrs['name'] = 'no-input-no-output'
                    return icon
                else:
                 # For a Library/Resource keyword the icon is necessary to set the return value
                 icon = Icon(settings.FA_ICONS.kw_call_only_output)
                 icon.attrs['name'] = 'only-output'
                 icon.attrs['style'].update({'filter': 'hue-rotate(150deg)'})
                 return icon
            else:
                icon = Icon(settings.FA_ICONS.kw_call_only_output, {'color': 'var(--keyta-secondary-color)'})
                icon.attrs['name'] = 'only-output'
                return icon

        if self.parameters.filter(user=user).count() != to_keyword_parameters_count:
            self.update_parameters(user)

        if has_return_values:
            icon = Icon(settings.FA_ICONS.kw_call_input_output)
            icon.attrs['name'] = 'input-output'
            return self.update_icon(icon, user)
        else:
            icon = Icon(settings.FA_ICONS.kw_call_only_input, {'color': 'var(--keyta-primary-color)'})
            icon.attrs['name'] = 'only-input'
            return self.update_icon(icon, user)

    def update_icon(self, icon: Icon, user: Optional[AbstractUser] = None):
        if self.has_empty_arg(user):
            icon.attrs['style'].update({'filter': 'hue-rotate(150deg)'})

        return icon

    @classmethod
    def get_substeps(cls, kw_calls: QuerySet):
        return (
            KeywordCall.unsorted()
            .filter(from_keyword__in=kw_calls.values_list('to_keyword'))
        )

    def get_previous_return_values(self) -> QuerySet:
        previous_kw_calls = []

        if self.from_keyword:
            previous_kw_calls = self.from_keyword.calls.filter(
                index__lt=self.index
            )

        if self.testcase:
            previous_kw_calls = self.testcase.steps.filter(
                index__lt=self.index
            )

        return (
            KeywordCallReturnValue.objects
            .filter(keyword_call__in=previous_kw_calls)
            .exclude(
                Q(kw_call_return_value__isnull=True) & Q(name__isnull=True)
            )
        )

    def has_empty_arg(self, user: Optional[AbstractUser]=None) -> bool:
        args: QuerySet = self.parameters.filter(user=user).args()
        arg: KeywordCallParameter
        for arg in args:
            if arg.is_empty():
                return True

    def has_no_kw_call(self):
        return not self.to_keyword

    def make_clone(self, attrs=None, sub_clone=False, using=None, parent=None):
        attrs = (attrs or {}) | {'clone': True}
        return super().make_clone(attrs, sub_clone, using, parent)

    def reset_parameters(self):
        param: KeywordCallParameter
        for param in self.parameters.all():
            if param.value_ref:
                param.reset_value()
                param.save()

    def save(
        self, force_insert=False, force_update=False,
        using=None, update_fields=None
    ):
        if not self.type:
            if self.testcase:
                self.type = KeywordCallType.TEST_STEP
            else:
                self.type = KeywordCallType.KEYWORD_CALL

        if not self.pk:
            super().save(force_insert, force_update, using, update_fields)

            if not hasattr(self, 'clone'):
                if self.to_keyword:
                    self.update_parameters()

                    for return_value in self.to_keyword.return_values.all():
                        self.add_return_value(return_value)
        else:
            if (
                not self.return_values.count() and
                self.to_keyword and
                (self.to_keyword.is_action or self.to_keyword.is_sequence)
            ):
                for return_value in self.to_keyword.return_values.all():
                    self.add_return_value(return_value)

            super().save(force_insert, force_update, using, update_fields)

    def to_robot(self, get_variable_value, user: Optional[AbstractUser]=None) -> RFKeywordCall:
        parameters = self.parameters.filter(user=user)
        varargs = parameters.filter(parameter__type=KeywordParameterType.VARARG)

        params = []

        for param in parameters:
            value = param.to_robot(get_variable_value) or '${EMPTY}'

            if param.parameter.is_arg or param.parameter.is_vararg:
                params.append(value)

            if param.parameter.is_kwarg:
                if varargs.exists():
                    if param.parameter.position > varargs.first().parameter.position:
                        params.append('%s=%s' % (param.name, value))
                    else:
                        params.append(value)
                else:
                    params.append('%s=%s' % (param.name, value))

        list_var = None

        if self.variable and self.variable.is_list():
            list_var = '@{%s}' % self.variable.name
            params = []

            param: KeywordCallParameter
            for param in parameters:
                if param.value_ref:
                    params.append('${row}[%s]' % str(param.value_ref))
                else:
                    if user_input := JSONValue.from_json(param.value).user_input:
                        params.append(user_input)

        return {
            'condition': ' and '.join([str(condition) for condition in self.conditions.all()]),
            'keyword': self.to_keyword.unique_name,
            'params': params,
            'return_values': [
                '${' + str(return_value) + '}'
                for return_value in self.return_values.all()
                if return_value.is_set
            ],
            'list_var': list_var
        }

    @classmethod
    def unsorted(cls):
        return KeywordCall.objects.order_by()

    def update_parameter_values(self):
        kw_call_param: KeywordCallParameter
        for kw_call_param in self.parameters.all():
            kw_call_param.update_value()

    def update_parameters(self, user: Optional[AbstractUser]=None):
        for param in self.to_keyword.parameters.exclude(type=KeywordParameterType.VARARG):
            self.add_parameter(param, user)

    class Manager(models.Manager):
        def get_queryset(self):
            return super().get_queryset()

        def keyword_calls(self):
            return (
                self
                .get_queryset()
                .only('index', 'from_keyword', 'to_keyword')
                .filter(type=KeywordCallType.KEYWORD_CALL)
            )

        def keyword_execution(self):
            return (
                self
                .get_queryset()
                .filter(type=KeywordCallType.KEYWORD_EXECUTION)
            )

        def suite_setup(self):
            return (
                self
                .get_queryset()
                .filter(type=SuiteSetupTeardown.SUITE_SETUP)
            )

        def suite_teardown(self):
            return (
                self
                .get_queryset()
                .filter(type=SuiteSetupTeardown.SUITE_TEARDOWN)
            )

        def test_setup(self):
            return (
                self
                .get_queryset()
                .filter(type=TestSetupTeardown.TEST_SETUP)
            )

        def test_steps(self):
            return (
                self
                .get_queryset()
                .filter(type=KeywordCallType.TEST_STEP)
            )

        def test_teardown(self):
            return (
                self
                .get_queryset()
                .filter(type=TestSetupTeardown.TEST_TEARDOWN)
            )

    objects = Manager()

    class Meta:
        ordering = ['index']
        verbose_name = _('Schritt')
        verbose_name_plural = _('Schritte')
        constraints = [
            UniqueConstraint(
                fields=['execution', 'type'],
                condition=Q(execution__isnull=False),
                name='unique_keyword_call_type_per_execution'
            )
        ]
