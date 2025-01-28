from typing import Optional

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext as _

from keyta.models.base_model import AbstractBaseModel
from keyta.rf_export.keywords import RFKeyword
from keyta.rf_export.testsuite import RFTestSuite

from apps.keywords.models import (
    KeywordCall,
    TestSetupTeardown,
    SuiteSetupTeardown
)
from apps.libraries.models import Library
from apps.resources.models import Resource

from .user_execution import UserExecution
from .execution_resource_import import ExecutionResourceImport
from .execution_library_import import ExecutionLibraryImport
from ..errors import ValidationError


class ExecutionType(models.TextChoices):
    KEYWORD = 'KEYWORD_EXECUTION', _('Schlüsselwort Ausführung')
    TESTCASE = 'TESTCASE_EXECUTION', _('Testfall Ausführung')


class Execution(AbstractBaseModel):
    keyword = models.OneToOneField(
        'keywords.Keyword',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        related_name='execution'
    )
    testcase = models.OneToOneField(
        'testcases.TestCase',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        related_name='execution'
    )
    type = models.CharField(max_length=255, choices=ExecutionType.choices)

    def __str__(self):
        return str(self.keyword or self.testcase)

    def get_testsuite(self, user: User):
        pass

    def save(
        self, force_insert=False, force_update=False, using=None,
            update_fields=None
    ):
        if not self.pk:
            if self.testcase:
                self.type = ExecutionType.TESTCASE
            if self.keyword:
                self.type = ExecutionType.KEYWORD

        super().save(force_insert, force_update, using, update_fields)

    def save_execution_result(self, user: User, robot_result: dict):
        user_exec, _ = UserExecution.objects.get_or_create(
            execution=self,
            user=user
        )
        user_exec.save_execution_result(robot_result)

    def suite_setup(self) -> Optional[KeywordCall]:
        return (
            self.keyword_calls
            .filter(type=SuiteSetupTeardown.SUITE_SETUP)
            .first()
        )

    def suite_teardown(self) -> Optional[KeywordCall]:
        return (
            self.keyword_calls
            .filter(type=SuiteSetupTeardown.SUITE_TEARDOWN)
            .first()
        )

    def test_setup(self, user: User) -> Optional[KeywordCall]:
        return (
            self.keyword_calls
            .filter(type=TestSetupTeardown.TEST_SETUP)
            .filter(user=user)
            .first()
        )

    def test_teardown(self, user: User) -> Optional[KeywordCall]:
        return (
            self.keyword_calls
            .filter(type=TestSetupTeardown.TEST_TEARDOWN)
            .filter(user=user)
            .first()
        )

    def to_robot(self, keywords: dict[int, RFKeyword], user: User) -> RFTestSuite:
        pass

    def update_library_imports(self, library_ids: set[int], user: User):
        for library in Library.objects.filter(id__in=library_ids):
            lib_import, created = ExecutionLibraryImport.objects.get_or_create(
                execution=self,
                library=library
            )
            lib_import.add_parameters(user)

        for lib_import in self.library_imports.exclude(library_id__in=library_ids):
            lib_import.delete()

    def update_resource_imports(self, resource_ids: set[int], user: User):
        for resource in Resource.objects.filter(id__in=resource_ids):
            resource_import, created = ExecutionResourceImport.objects.get_or_create(
                execution=self,
                resource=resource
            )

        for resource_import in self.resource_imports.exclude(resource_id__in=resource_ids):
            resource_import.delete()

    def validate(self, user: User) -> Optional[ValidationError]:
        pass

    class Meta:
        constraints = [
            models.CheckConstraint(
                name='execution_sum_type',
                check=
                (Q(type=ExecutionType.KEYWORD) &
                 Q(keyword__isnull=False) &
                 Q(testcase__isnull=True))
                |
                (Q(type=ExecutionType.TESTCASE) &
                 Q(keyword__isnull=True) &
                 Q(testcase__isnull=False))
            )
        ]
        verbose_name = _('Ausführung')
        verbose_name_plural = _('Ausführung')
