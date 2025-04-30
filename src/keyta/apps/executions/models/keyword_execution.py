from typing import Optional

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _

from keyta.apps.keywords.models import (
    Keyword,
    KeywordCall,
    TestSetupTeardown
)
from keyta.apps.keywords.models.keyword import KeywordType
from keyta.apps.keywords.models.keywordcall import KeywordCallType
from keyta.rf_export.testsuite import RFTestSuite

from ..errors import ValidationError
from .execution import Execution, ExecutionType


class KeywordExecution(Execution):
    @property
    def action_ids(self) -> list[int]:
        if self.keyword.is_sequence:
            return list(
                self.keyword.calls
                .filter(to_keyword__resource__isnull=True)
                .values_list('to_keyword', flat=True)
            )

        return []

    def add_attach_to_system(self, user: AbstractUser):
        attach_to_system_id = (
            self.keyword.systems
            .values_list('attach_to_system', flat=True)
            .distinct()
            .first()
        )

        if attach_to_system_id:
            attach_to_system = Keyword.objects.get(
                id=attach_to_system_id
            )
            kw_call, created = KeywordCall.objects.get_or_create(
                execution=self,
                type=TestSetupTeardown.TEST_SETUP,
                to_keyword=attach_to_system
            )

            for param in attach_to_system.parameters.all():
                kw_call.add_parameter(param, user)

    @property
    def execution_keyword_call(self) -> Optional[KeywordCall]:
        return (
            self.keyword_calls
            .filter(type=KeywordCallType.KEYWORD_EXECUTION)
            .first()
        )

    def get_keyword_calls(self) -> models.QuerySet:
        if self.keyword.type == KeywordType.SEQUENCE:
            sequence_calls = KeywordCall.unsorted().filter(from_keyword=self.keyword)
            action_calls = KeywordCall.get_substeps(sequence_calls)
        
        if self.keyword.type == KeywordType.ACTION:
            sequence_calls = models.QuerySet().none()
            action_calls = KeywordCall.unsorted().filter(from_keyword=self.keyword)
        
        setup_teardown_calls = KeywordCall.get_substeps(self.keyword_calls)
        
        return sequence_calls | action_calls | setup_teardown_calls

    def get_rf_testsuite(self, user: AbstractUser) -> RFTestSuite:
        keyword = self.keyword
        keywords = {keyword.pk: keyword.to_robot()}

        if keyword.is_sequence:
            for keyword in Keyword.objects.filter(pk__in=self.action_ids):
                keywords[keyword.pk] = keyword.to_robot()

        if (test_setup := self.test_setup()) and test_setup.enabled:
            if to_keyword := test_setup.to_keyword:
                action = Keyword.objects.get(id=to_keyword.id)
                keywords[action.id] = action.to_robot()

        return {
            'name': self.keyword.name,
            'settings': self.get_rf_settings(user),
            'dict_variables': [],
            'list_variables': [],
            'keywords': list(keywords.values()),
            'testcases': [{
                'name': _('Test'),
                'doc': None,
                'steps': [
                    self.execution_keyword_call.to_robot(user)
                ]
            }]
        }

    def save(
        self, force_insert=False, force_update=False, using=None,
            update_fields=None
    ):
        self.type = ExecutionType.KEYWORD
        super().save(force_insert, force_update, using, update_fields)

    def validate(self, user: AbstractUser) -> Optional[dict]:
        return (self.validate_keyword_call(user) or
                self.validate_test_setup(user) or
                self.validate_steps()
                )

    def validate_keyword_call(self, user: AbstractUser) -> Optional[dict]:
        if self.execution_keyword_call.has_empty_arg(user):
            return ValidationError.INCOMPLETE_CALL_PARAMS

        return None

    def validate_steps(self) -> Optional[dict]:
        if any(call.has_empty_arg() for call in self.keyword.calls.all()):
            return ValidationError.INCOMPLETE_STEP_PARAMS

        return None

    def validate_test_setup(self, user: AbstractUser) -> Optional[dict]:
        test_setup: KeywordCall = self.test_setup()

        if not test_setup:
            self.add_attach_to_system(user)

        if test_setup.has_empty_arg(user):
            return ValidationError.INCOMPLETE_ATTACH_TO_SYSTEM_PARAMS

        return None

    class Manager(models.Manager):
        def get_queryset(self):
            return (
                super()
                .get_queryset()
                .filter(type=ExecutionType.KEYWORD)
            )

    objects = Manager()

    class Meta:
        proxy = True
        verbose_name = _('Ausführung')
        verbose_name_plural = _('Ausführung')
