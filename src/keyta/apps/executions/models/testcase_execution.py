from typing import Optional

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from keyta.apps.keywords.models import Keyword, KeywordCall, TestStep
from keyta.apps.variables.models import Variable, VariableInList
from keyta.rf_export.testsuite import RFTestSuite

from ..errors import ValidationError
from .execution import Execution, ExecutionType


class TestCaseExecution(Execution):
    @property
    def action_ids(self):
        return (
            KeywordCall.objects
            .filter(from_keyword__in=self.sequence_ids)
            .filter(to_keyword__resource__isnull=True)
            .values_list('to_keyword', flat=True)
        )

    @property
    def sequence_ids(self):
        return (
            KeywordCall.objects
            .filter(testcase_id=self.testcase.pk)
            .filter(to_keyword__resource__isnull=True)
            .values_list('to_keyword', flat=True)
        )

    @property
    def window_ids(self):
        return (
            KeywordCall.objects
            .filter(testcase_id=self.testcase.pk)
            .values_list('window_id', flat=True)
            .distinct()
        )

    def get_keyword_calls(self) -> models.QuerySet:
        setup_teardown_calls = KeywordCall.get_substeps(self.keyword_calls)
        test_calls = KeywordCall.unsorted().filter(testcase=self.testcase)
        sequence_calls = KeywordCall.get_substeps(test_calls)
        action_calls = KeywordCall.get_substeps(sequence_calls)
        
        return setup_teardown_calls | test_calls | sequence_calls | action_calls

    def get_rf_testsuite(self, user: AbstractUser) -> RFTestSuite:
        keywords = {
            keyword.pk: keyword.to_robot()
            for keyword in
            Keyword.objects.filter(pk__in=self.sequence_ids|self.action_ids)
        }

        if (test_setup := self.test_setup()) and test_setup.enabled:
            if to_keyword := test_setup.to_keyword:
                keywords[to_keyword.id] = to_keyword.to_robot()

        if (test_teardown := self.test_teardown()) and test_teardown.enabled:
            if to_keyword := test_teardown.to_keyword:
                keywords[to_keyword.id] = to_keyword.to_robot()

        dict_variables = []
        list_variables = []

        step: TestStep
        for step in self.testcase.steps.all():
            variable: Variable = step.variable
            if variable and variable.is_list():
                list_variables.append(variable.to_robot())

                element: VariableInList
                for element in variable.elements.all():
                    dict_variables.append(element.variable.to_robot())

        return {
            'name': self.testcase.name,
            'settings': self.get_rf_settings(user),
            'dict_variables': dict_variables,
            'list_variables': list_variables,
            'keywords': list(keywords.values()),
            'testcases': [self.testcase.to_robot()]
        }

    def save(
        self, force_insert=False, force_update=False, using=None,
            update_fields=None
    ):
        self.type = ExecutionType.TESTCASE
        super().save(force_insert, force_update, using, update_fields)

    def validate(self, user: AbstractUser) -> Optional[ValidationError]:
        if not self.testcase.steps.count():
            return ValidationError.NO_STEPS

        step: TestStep
        for step in self.testcase.steps.all():
            if step.has_no_kw_call():
                return ValidationError.INCOMPLETE_STEP

            if step.has_empty_arg():
                return ValidationError.INCOMPLETE_STEP_PARAMS

        test_setup: KeywordCall = self.test_setup()
        test_teardown: KeywordCall = self.test_teardown()

        if test_setup and test_setup.has_empty_arg(user):
           return ValidationError.INCOMPLETE_TEST_SETUP_PARAMS

        if test_teardown and test_teardown.has_empty_arg(user):
            return ValidationError.INCOMPLETE_TEST_TEARDOWN_PARAMS

        return None

    class Manager(models.Manager):
        def get_queryset(self):
            return (
                super()
                .get_queryset()
                .filter(type=ExecutionType.TESTCASE)
            )

    objects = Manager()

    class Meta:
        proxy = True
        verbose_name = _('Ausführung')
        verbose_name_plural = _('Ausführung')
