from typing import Optional
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from apps.actions.models import Action
from apps.executions.errors import ValidationError
from apps.executions.models import Execution
from apps.keywords.models import KeywordCall, KeywordType
from apps.libraries.models import LibraryImport
from apps.rf_export.keywords import RFKeyword
from apps.rf_export.testsuite import RFTestSuite
from apps.sequences.models import Sequence


class TestCaseExecution(Execution):
    def get_testsuite(self, user: User) -> RFTestSuite:
        keywords = {}

        test_step: KeywordCall
        for test_step in self.testcase.steps.all():
            sequence = Sequence.objects.get(id=test_step.to_keyword.pk)
            keywords[sequence.id] = sequence.to_robot()

            for action in sequence.actions:
                keywords[action.id] = action.to_robot()

        return self.to_robot(keywords, user)

    def to_robot(self, keywords: dict[int, RFKeyword], user: User) -> RFTestSuite:
        def maybe_to_robot(keyword_call: KeywordCall, user: User):
            if keyword_call and keyword_call.enabled:
                return keyword_call.to_robot(user)

        if (test_setup := self.test_setup(user)) and test_setup.enabled:
            to_keyword = test_setup.to_keyword

            if to_keyword.type == KeywordType.ACTION:
                action = Action.objects.get(id=to_keyword.id)
                keywords[action.id] = action.to_robot()

        if (test_teardown := self.test_teardown(user)) and test_teardown.enabled:
            to_keyword = test_teardown.to_keyword

            if to_keyword.type == KeywordType.ACTION:
                action = Action.objects.get(id=to_keyword.id)
                keywords[action.id] = action.to_robot()

        return {
            'name': self.testcase.name,
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
                'test_teardown': maybe_to_robot(test_teardown, user),
            },
            'keywords': list(keywords.values()),
            'testcases': [
                self.testcase.to_robot()
            ]
        }

    def update_library_imports(self, library_ids: set[int], user: User):
        sequence_ids = KeywordCall.objects.filter(testcase_id=self.testcase.pk).values_list('to_keyword_id')
        action_ids = KeywordCall.objects.filter(from_keyword_id__in=sequence_ids).values_list('to_keyword_id')

        for lib_id in LibraryImport.objects.filter(keyword_id__in=action_ids).values_list('library_id').distinct():
            library_ids.update(lib_id)

        test_setup = self.test_setup(user)
        test_teardown = self.test_teardown(user)

        if test_setup and test_setup.to_keyword.type == KeywordType.ACTION:
            action = Action.objects.get(pk=test_setup.to_keyword.pk)
            library_ids.update(action.library_ids)

        if test_teardown and test_teardown.to_keyword.type == KeywordType.ACTION:
            action = Action.objects.get(pk=test_teardown.to_keyword.pk)
            library_ids.update(action.library_ids)

        super().update_library_imports(library_ids, user)

    def update_resource_imports(self, resource_ids: set[int], user: User):
        sequences = Sequence.objects.filter(id__in=self.testcase.steps.values_list('to_keyword_id'))

        for sequence in sequences:
            resource_ids.update(sequence.resource_ids)

        super().update_resource_imports(resource_ids, user)

    def validate(self, user: User) -> Optional[ValidationError]:
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
