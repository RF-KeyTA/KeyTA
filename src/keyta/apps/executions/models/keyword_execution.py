from typing import Optional
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from apps.actions.models import Action
from apps.keywords.models import (
    KeywordCallType,
    KeywordCall,
    KeywordType,
    TestSetupTeardown
)
from apps.rf_export.keywords import RFKeyword
from apps.rf_export.testsuite import RFTestSuite

from .execution import Execution
from ..errors import ValidationError


class KeywordExecution(Execution):
    def add_attach_to_system(self, user: User):
        attach_to_system_id = (
            self.keyword.systems
            .values_list('attach_to_system', flat=True)
            .distinct()
            .first()
        )

        if attach_to_system_id:
            attach_to_system = Action.objects.get(
                id=attach_to_system_id
            )
            kw_call = KeywordCall.objects.create(
                execution=self,
                type=TestSetupTeardown.TEST_SETUP,
                user=user,
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

    def test_setup(self, user: User) -> Optional[KeywordCall]:
        test_setup = super().test_setup(user)

        if not test_setup:
            self.add_attach_to_system(user)
            return super().test_setup(user)

        return test_setup

    def to_robot(self, keywords: dict[int, RFKeyword], user: User) -> RFTestSuite:
        def maybe_to_robot(keyword_call: KeywordCall, user: User):
            if keyword_call and keyword_call.enabled:
                return keyword_call.to_robot(user)

        if (test_setup := self.test_setup(user)) and test_setup.enabled:
            to_keyword = test_setup.to_keyword

            if to_keyword.type == KeywordType.ACTION:
                action = Action.objects.get(id=to_keyword.id)
                keywords[action.id] = action.to_robot()

        return {
            'name': self.keyword.name,
            'settings': {
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
                'test_setup': maybe_to_robot(test_setup, user),
                'test_teardown': None
            },
            'keywords': list(keywords.values()),
            'testcases': [
                {
                    'name': _('Test'),
                    'doc': None,
                    'steps': [
                        self.execution_keyword_call.to_robot(user)
                    ]
                }
            ]
        }

    def update_library_imports(self, library_ids: set[int], user: User):
        test_setup = self.test_setup(user)

        if test_setup and test_setup.to_keyword.type == KeywordType.ACTION:
            action = Action.objects.get(pk=test_setup.to_keyword.pk)
            library_ids.update(action.library_ids)

        super().update_library_imports(library_ids, user)

    def validate(self, user: User) -> Optional[ValidationError]:
        return (self.validate_keyword_call(user) or
                self.validate_test_setup(user) or
                self.validate_steps()
                )

    def validate_keyword_call(self, user: User) -> Optional[ValidationError]:
        keyword_parameters = self.keyword.parameters
        keyword_call = self.execution_keyword_call
        keyword_call_parameters = keyword_call.parameters.filter(user=user)

        if ((keyword_parameters.count() != keyword_call_parameters.count()) or
                keyword_call.has_empty_arg(user)
        ):
            return ValidationError.INCOMPLETE_CALL_PARAMS

        return None

    def validate_steps(self) -> Optional[ValidationError]:
        for call in self.keyword.calls.all():
            if call.has_empty_arg():
                return ValidationError.INCOMPLETE_STEP_PARAMS

        return None

    def validate_test_setup(self, user: User) -> Optional[ValidationError]:
        test_setup = self.test_setup(user)

        if not test_setup:
            self.add_attach_to_system(user)
        else:
            if test_setup.has_empty_arg(user):
                return ValidationError.INCOMPLETE_ATTACH_TO_SYSTEM_PARAMS

        return None

    class Meta:
        proxy = True
        verbose_name = _('Ausführung')
        verbose_name_plural = _('Ausführung')
