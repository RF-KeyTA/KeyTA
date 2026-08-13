from typing import TypedDict, Optional

from django.db.models import QuerySet

from .keywords import RFKeyword, RFKeywordCall
from .settings import RFSettings
from .testcases import RFTestCase


class RFTestSuite(TypedDict):
    name: str
    settings: RFSettings
    keywords: dict[int, RFKeyword]
    testcases: list[RFTestCase]


def make_rf_testsuite(name: str, testcases: QuerySet, testcase_to_testsuite, suite_setup: Optional[RFKeywordCall]=None) -> RFTestSuite:
    testsuite: RFTestSuite = {
        'name': name,
        'settings': {
            'documentation': None,
            'library_imports': {},
            'metadata': {},
            'resource_imports': {},
            'suite_setup': suite_setup,
            'suite_teardown': None
        },
        'keywords': {},
        'testcases': []
    }

    for testcase in testcases.all():
        rf_testsuite: RFTestSuite = testcase_to_testsuite(testcase)
        testsuite['settings']['library_imports'].update(rf_testsuite['settings']['library_imports'])
        testsuite['settings']['resource_imports'].update(rf_testsuite['settings']['resource_imports'])
        testsuite['keywords'].update(rf_testsuite['keywords'])
        testsuite['testcases'].extend(rf_testsuite['testcases'])

    return testsuite
