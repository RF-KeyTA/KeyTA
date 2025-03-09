from typing import Optional

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, QuerySet
from django.utils.translation import gettext as _

from model_clone import CloneMixin

from keyta.apps.libraries.models import Library, LibraryImport
from keyta.apps.resources.models import Resource, ResourceImport
from keyta.models.base_model import AbstractBaseModel
from keyta.rf_export.testsuite import RFTestSuite
from keyta.rf_export.settings import RFSettings

from .user_execution import UserExecution


class ExecutionType(models.TextChoices):
    KEYWORD = 'KEYWORD_EXECUTION', _('Schlüsselwort Ausführung')
    TESTCASE = 'TESTCASE_EXECUTION', _('Testfall Ausführung')


class Execution(CloneMixin, AbstractBaseModel):
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
    type = models.CharField(max_length=255)

    _clone_m2o_or_o2m_fields = ['keyword_calls']

    def __str__(self):
        return str(self.keyword or self.testcase)

    def get_library_dependencies(self) -> QuerySet:
        pass

    def get_resource_dependencies(self) -> list[int]:
        pass

    def get_rf_settings(self, user: AbstractUser) -> RFSettings:
        def maybe_to_robot(keyword_call, user: AbstractUser):
            if keyword_call and keyword_call.enabled:
                return keyword_call.to_robot(user)

        return {
            'library_imports': [
                lib_import.to_robot(user)
                for lib_import
                in self.library_imports.all()
            ],
            'resource_imports': [
                resource_import.to_robot(user)
                for resource_import
                in self.resource_imports.all()
            ],
            'suite_setup': None,
            'suite_teardown': None,
            'test_setup': maybe_to_robot(self.test_setup(), user),
            'test_teardown': maybe_to_robot(self.test_teardown(), user)
        }

    def get_rf_testsuite(self, user: AbstractUser) -> RFTestSuite:
        pass

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.type:
            if self.testcase:
                self.type = ExecutionType.TESTCASE
            if self.keyword:
                self.type = ExecutionType.KEYWORD

        if self.type == ExecutionType.TESTCASE:
            self.keyword = None

        if self.type == ExecutionType.KEYWORD:
            self.testcase = None

        super().save(force_insert, force_update, using, update_fields)

    def save_execution_result(self, user: AbstractUser, robot_result: dict):
        user_exec, _ = UserExecution.objects.get_or_create(
            execution=self,
            user=user
        )
        user_exec.save_execution_result(robot_result)

    def suite_setup(self):
        return (
            self.keyword_calls
            .suite_setup()
            .first()
        )

    def suite_teardown(self):
        return (
            self.keyword_calls
            .suite_teardown()
            .first()
        )

    def test_setup(self):
        return (
            self.keyword_calls
            .test_setup()
            .first()
        )

    def test_teardown(self):
        return (
            self.keyword_calls
            .test_teardown()
            .first()
        )

    def update_library_imports(self, user: AbstractUser):
        library_ids = self.get_library_dependencies()

        if test_setup := self.test_setup():
            library_ids |= LibraryImport.objects.filter(keyword=test_setup.to_keyword).library_ids()

        if test_teardown := self.test_teardown():
            library_ids |= LibraryImport.objects.filter(keyword=test_teardown.to_keyword).library_ids()

        for library in Library.objects.filter(id__in=library_ids):
            lib_import, created = LibraryImport.objects.get_or_create(
                execution=self,
                library=library
            )
            lib_import.add_parameters(user)

        for lib_import in self.library_imports.exclude(library_id__in=library_ids):
            lib_import.delete()

    def update_resource_imports(self):
        if Resource.objects.count():
            if resource_ids := self.get_resource_dependencies():
                for resource in Resource.objects.filter(id__in=resource_ids):
                    ResourceImport.objects.get_or_create(
                        execution=self,
                        resource=resource
                    )

                for resource_import in self.resource_imports.exclude(resource_id__in=resource_ids):
                    resource_import.delete()

    def validate(self, user: AbstractUser) -> Optional[dict]:
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
