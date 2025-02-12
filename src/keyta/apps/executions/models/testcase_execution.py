from typing import Optional

from django.contrib.auth.models import AbstractUser
from django.db.models import QuerySet
from django.utils.translation import gettext as _

from keyta.apps.keywords.models import Keyword, KeywordCall
from keyta.apps.libraries.models import LibraryImport
from keyta.apps.resources.models import Resource, ResourceImport
from keyta.rf_export.testsuite import RFTestSuite

from ..errors import ValidationError
from .execution import Execution, ExecutionType


class TestCaseExecution(Execution):
    @property
    def action_ids(self):
        return (
            KeywordCall.objects
            .filter(from_keyword__in=self.sequence_ids)
            .values_list('to_keyword', flat=True)
        )

    @property
    def sequence_ids(self):
        return (
            KeywordCall.objects
            .filter(testcase_id=self.testcase.pk)
            .values_list('to_keyword', flat=True)
        )

    def get_library_dependencies(self) -> QuerySet:
        return (
            LibraryImport.objects
            .filter(keyword__id__in=[self.action_ids])
            .library_ids()
        )

    def get_resource_dependencies(self) -> QuerySet:
        if Resource.objects.count():
            return (
                ResourceImport.objects
                .filter(keyword__id__in=[self.sequence_ids])
                .resource_ids()
            )

        return QuerySet()

    def get_rf_testsuite(self, user: AbstractUser) -> RFTestSuite:
        keywords = {
            keyword.pk: keyword.to_robot() # keyword.get_admin_url()
            for keyword in
            Keyword.objects.filter(pk__in=self.sequence_ids|self.action_ids)
        }

        if (test_setup := self.test_setup(user)) and test_setup.enabled:
            if to_keyword := test_setup.to_keyword:
                keywords[to_keyword.id] = to_keyword.to_robot() # to_keyword.get_admin_url()

        if (test_teardown := self.test_teardown(user)) and test_teardown.enabled:
            if to_keyword := test_teardown.to_keyword:
                keywords[to_keyword.id] = to_keyword.to_robot()  # to_keyword.get_admin_url()

        return {
            'name': self.testcase.name,
            'settings': self.get_rf_settings(user),
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
        if any(step.has_empty_arg() for step in self.testcase.steps.all()):
            return ValidationError.INCOMPLETE_STEP_PARAMS

        test_setup = self.test_setup(user)
        test_teardown = self.test_teardown(user)

        if test_setup and test_setup.has_empty_arg(user):
           return ValidationError.INCOMPLETE_TEST_SETUP_PARAMS

        if test_teardown and test_teardown.has_empty_arg(user):
            return ValidationError.INCOMPLETE_TEST_TEARDOWN_PARAMS

        return None

    class Meta:
        proxy = True
        verbose_name = _('Ausführung')
        verbose_name_plural = _('Ausführung')
