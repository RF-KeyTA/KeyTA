from typing import Optional
from django.db import models
from django.db.models import Q, QuerySet
from django.contrib.auth.models import User

from apps.common.abc import AbstractBaseModel
from apps.rf_export.keywords import RFKeywordCall


from .keywordcall_return_value import KeywordCallReturnValue
from .keywordcall_parameters import KeywordCallParameter, jsonify
from .keyword import Keyword
from .keyword_parameters import KeywordParameter
from .keyword_return_value import KeywordReturnValue


class TestSetupTeardown(models.TextChoices):
    TEST_SETUP = 'TEST_SETUP', 'Testvorbereitung'
    TEST_TEARDOWN = 'TEST_TEARDOWN', 'Testnachbereitung'


class SuiteSetupTeardown(models.TextChoices):
    SUITE_SETUP = 'SUITE_SETUP', 'Suitevorbereitung'
    SUITE_TEARDOWN = 'SUITE_TEARDOWN', 'Suitenachbereitung'


class KeywordCallType(models.TextChoices):
    KEYWORD_CALL = 'KEYWORD_CALL', 'Schlüsselwort-Aufruf'
    KEYWORD_EXECUTION = 'KEYWORD_EXECUTION', 'Schlüsselwort Ausführung'
    TEST_STEP = 'TEST_STEP', 'Testschritt'


class KeywordCall(AbstractBaseModel):
    from_keyword = models.ForeignKey(
        Keyword,
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
        Keyword,
        on_delete=models.CASCADE,
        related_name='uses'
    )
    enabled = models.BooleanField(default=True, verbose_name='')
    index = models.PositiveSmallIntegerField(default=0, db_index=True)
    type = models.CharField(
        max_length=255,
        choices=KeywordCallType.choices +
        TestSetupTeardown.choices +
        SuiteSetupTeardown.choices
    )
    # Test/Suite Setup/Teardown are user-dependent
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True
    )

    # --Customization--
    # In a TestCase keyword calls depend on the selected Window
    window = models.ForeignKey(
        'windows.Window',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        blank=True,
        verbose_name='Maske'
    )

    def __str__(self):
        return str(self.caller) + ' → ' + str(self.to_keyword)

    def add_parameter(
        self,
        param: KeywordParameter,
        user: Optional[User]=None
    ):
        KeywordCallParameter.objects.get_or_create(
            keyword_call=self,
            parameter=param,
            user=user,
            defaults={
                'value': jsonify(param.default_value, None),
            }
        )

    @property
    def caller(self):
        if self.pk:
            return self.from_keyword or self.testcase or self.execution
        return None

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
                Q(return_value__isnull=True) & Q(name__isnull=True)
            )
        )

    def has_empty_arg(self, user: Optional[User]=None) -> bool:
        args: QuerySet = self.parameters.filter(user=user).args()
        return any(arg.current_value is None for arg in args)

    def save(
        self, force_insert=False, force_update=False,
        using=None, update_fields=None
    ):
        if not self.type:
            self.type = KeywordCallType.KEYWORD_CALL

        if not self.pk:
            super().save(force_insert, force_update, using, update_fields)

            if self.type in [
                KeywordCallType.KEYWORD_CALL, KeywordCallType.TEST_STEP
            ]:
                for param in self.to_keyword.parameters.all():
                    self.add_parameter(param)

                return_value: KeywordReturnValue
                return_value = self.to_keyword.return_value.first()

                if return_value:
                    KeywordCallReturnValue.objects.create(
                        keyword_call=self,
                        return_value=return_value.kw_call_return_value
                    )
        else:
            return super().save(force_insert, force_update, using, update_fields)

    def to_robot(self, user: Optional[User]=None) -> RFKeywordCall:
        args = self.parameters.filter(user=user).args()
        kwargs = self.parameters.filter(user=user).kwargs()
        return_value: KeywordCallReturnValue = self.return_value.first()

        return {
            'keyword': self.to_keyword.unique_name,
            'args': [arg.to_robot() for arg in args],
            'kwargs': {kwarg.name: kwarg.to_robot() for kwarg in kwargs},
            'return_value': (
                '${' + str(return_value) + '}'
                if return_value and return_value.is_set
                else None
            )
        }

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
        verbose_name = 'Schritt'
        verbose_name_plural = 'Schritte'
        constraints = [
            models.CheckConstraint(
                name='keyword_call_sum_type',
                check=
                (Q(type=KeywordCallType.KEYWORD_CALL) &
                 Q(from_keyword__isnull=False) &
                 Q(execution__isnull=True) &
                 Q(testcase__isnull=True) &
                 Q(window__isnull=True))
                |
                (Q(type=KeywordCallType.TEST_STEP) &
                 Q(testcase__isnull=False) &
                 Q(window__isnull=False) &
                 Q(execution__isnull=True) &
                 Q(from_keyword__isnull=True))
                |
                (Q(type=KeywordCallType.KEYWORD_EXECUTION) &
                 Q(execution__isnull=False) &
                 Q(from_keyword__isnull=True) &
                 Q(testcase__isnull=True) &
                 Q(window__isnull=True))
                |
                (Q(type=TestSetupTeardown.TEST_SETUP) &
                 Q(execution__isnull=False) &
                 Q(from_keyword__isnull=True) &
                 Q(testcase__isnull=True) &
                 Q(window__isnull=True))
                |
                (Q(type=TestSetupTeardown.TEST_TEARDOWN) &
                 Q(execution__isnull=False) &
                 Q(from_keyword__isnull=True) &
                 Q(testcase__isnull=True) &
                 Q(window__isnull=True))
                |
                (Q(type=SuiteSetupTeardown.SUITE_SETUP) &
                 Q(execution__isnull=False) &
                 Q(from_keyword__isnull=True) &
                 Q(testcase__isnull=True) &
                 Q(window__isnull=True))
                |
                (Q(type=SuiteSetupTeardown.SUITE_TEARDOWN) &
                 Q(execution__isnull=False) &
                 Q(from_keyword__isnull=True) &
                 Q(testcase__isnull=True) &
                 Q(window__isnull=True))
            )
        ]
