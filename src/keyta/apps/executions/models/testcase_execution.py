from typing import Optional

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from keyta.apps.keywords.models import (
    Keyword,
    KeywordCall,
    KeywordCallParameter,
    KeywordCallParameterSource
)
from keyta.apps.testcases.models import TestStep
from keyta.apps.variables.models import Variable
from keyta.rf_export.testsuite import RFTestSuite

from ..errors import ValidationError
from .execution import Execution, ExecutionType


class TestCaseExecution(Execution):
    def action_ids(self, sequence_pks):
        return (
            KeywordCall.objects
            .filter(from_keyword__in=sequence_pks)
            .filter(to_keyword__resource__isnull=True)
            .values_list('to_keyword', flat=True)
        )

    def sequence_ids(self, test_steps):
        return (
            test_steps
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

    def get_rf_testsuite(self, get_variable_value, user: AbstractUser, execution_state: dict) -> RFTestSuite:
        sequence_pks = self.sequence_ids(self.testcase.executable_steps(execution_state))

        keywords = {
            keyword.pk: keyword.to_robot(get_variable_value, {})
            for keyword in
            Keyword.objects
            .prefetch_related('parameters')
            .prefetch_related('return_values')
            .prefetch_related('calls')
            .filter(pk__in=sequence_pks | self.action_ids(sequence_pks))
        }
        attach_to_running_system = self.test_setup().first()

        if execution_state.get('BEGIN_EXECUTION'):
            attach_to_running_system.enabled = True
            attach_to_running_system.save()
        else:
            attach_to_running_system.enabled = False
            attach_to_running_system.save()

        if test_setup := self.test_setup().filter(enabled=True).first():
            if to_keyword := test_setup.to_keyword:
                keywords[to_keyword.id] = to_keyword.to_robot(get_variable_value, {})

        if test_teardown := self.test_teardown().first():
            if to_keyword := test_teardown.to_keyword:
                keywords[to_keyword.id] = to_keyword.to_robot(get_variable_value, {})

        tables, rows = self.get_tables_rows()

        return {
            'name': self.testcase.name,
            'settings': self.get_rf_settings(get_variable_value, user, execution_state),
            'variables': [*tables, *rows],
            'keywords': list(keywords.values()),
            'testcases': [self.testcase.to_robot(get_variable_value, user, execution_state)]
        }

    def get_tables_rows(self):
        table_variables = []
        row_variables = []

        value_ref_pks = (
            KeywordCallParameter.objects
            .filter(keyword_call__in=self.testcase.steps.all())
            .filter(value_ref__isnull=False)
            .values_list('value_ref', flat=True)
        )

        table_pks = (
            KeywordCallParameterSource.objects
            .filter(pk__in=value_ref_pks)
            .filter(table_column__isnull=False)
            .values_list('table_column__table', flat=True)
            .distinct()
        )

        for table in Variable.objects.filter(pk__in=table_pks):
            table_variable, table_row_variables = table.get_rows()
            table_variables.append(table_variable)
            row_variables.extend(table_row_variables)

        return table_variables, row_variables

    def save(
        self, force_insert=False, force_update=False, using=None,
            update_fields=None
    ):
        self.type = ExecutionType.TESTCASE
        super().save(force_insert, force_update, using, update_fields)

    def validate(self, user: AbstractUser, execution_state: dict) -> Optional[ValidationError]:
        if not self.testcase.steps.count():
            return ValidationError.NO_STEPS

        test_steps = self.testcase.executable_steps(execution_state)

        step: TestStep
        for step in test_steps:
            if step.has_empty_arg(user):
                return ValidationError.INCOMPLETE_STEP_PARAMS

        test_setup: KeywordCall = self.test_setup().filter(enabled=True).first()
        test_teardown: KeywordCall = self.test_teardown().filter(enabled=True).first()

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
