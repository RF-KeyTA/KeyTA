from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from model_clone import CloneMixin

from keyta.apps.keywords.models.keyword import KeywordType
from keyta.apps.libraries.models import Library, LibraryImport
from keyta.apps.resources.models import Resource, ResourceImport
from keyta.models.base_model import AbstractBaseModel
from keyta.rf_export.rfgenerator import gen_testsuite
from keyta.rf_export.settings import RFSettings
from keyta.rf_export.testsuite import RFTestSuite
from keyta.widgets import Icon

from .user_execution import UserExecution


@dataclass
class Dependencies:
    libraries: set[int]
    resources: set[int]


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

    def get_keyword_calls(self) -> models.QuerySet:
        return models.QuerySet().none()

    def get_keyword_dependencies(self) -> Dependencies:
        dependencies = Dependencies(
            libraries = set(),
            resources = set(),
        )
        lib_res = (
            self.get_keyword_calls()
            .filter(to_keyword__type__in=[KeywordType.LIBRARY, KeywordType.RESOURCE])
            .values_list('to_keyword__library', 'to_keyword__resource')
        )

        for library, resource in lib_res:
            if library:
                dependencies.libraries.add(library)
            
            if resource:
                dependencies.resources.add(resource)

        return dependencies

    def get_log_icon(self, user: AbstractUser):
        user_exec = self.user_execs.get(user=user)

        if user_exec.result and not user_exec.running:
            url = 'http://localhost:1471/' + user_exec.log
            title = str(Icon(settings.FA_ICONS.exec_log))
            return '<a href="%s" id="log-btn" target="_blank">%s</a>' % (url, title)

        return '-'

    def get_result_icon(self, user: AbstractUser):
        user_exec = self.user_execs.get(user=user)

        if (result := user_exec.result) and not user_exec.running:
            if result == 'FAIL':
                icon = Icon(
                    settings.FA_ICONS.exec_fail,
                    {'color': 'red'}
                )
                return str(icon)

            if result == 'PASS':
                icon = Icon(
                    settings.FA_ICONS.exec_pass,
                    {'color': 'green'}
                )
                return str(icon)

        return '-'

    def get_rf_settings(self, user: AbstractUser) -> RFSettings:
        return {
            'library_imports': {
                lib_import.library.pk: lib_import.to_robot(user)
                for lib_import
                in self.library_imports.all()
            },
            'resource_imports': {
                resource_import.resource.pk: resource_import.to_robot(user)
                for resource_import
                in self.resource_imports.all()
            },
            'suite_setup': None,
            'suite_teardown': None,
        }

    def get_rf_testsuite(self, get_variable_value, user: AbstractUser, execution_state: dict) -> RFTestSuite:
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

    def test_setup(self) -> QuerySet:
        return (
            self.keyword_calls
            .test_setup()
        )

    def test_teardown(self) -> QuerySet:
        return (
            self.keyword_calls
            .test_teardown()
        )

    def to_robot(self, get_variable_value, user: AbstractUser, execution_state: dict) -> dict:
        testsuite = self.get_rf_testsuite(get_variable_value, user, execution_state)

        return {
            'testsuite_name': testsuite['name'],
            'testsuite': gen_testsuite(testsuite)
        }

    def update_imports(self, user: AbstractUser):
        dependencies = self.get_keyword_dependencies()
        
        for library in Library.objects.filter(id__in=dependencies.libraries):
            lib_import, created = LibraryImport.objects.get_or_create(
                execution=self,
                library=library
            )
            lib_import.add_parameters(user)

        for lib_import in self.library_imports.exclude(library_id__in=dependencies.libraries):
            lib_import.delete()

        for resource in Resource.objects.filter(id__in=dependencies.resources):
            ResourceImport.objects.get_or_create(
                execution=self,
                resource=resource
            )

        for resource_import in self.resource_imports.exclude(resource_id__in=dependencies.resources):
            resource_import.delete()

    def validate(self, user: AbstractUser, execution_state: dict) -> Optional[dict]:
        pass

    class Meta:
        verbose_name = _('Ausführung')
        verbose_name_plural = _('Ausführung')
