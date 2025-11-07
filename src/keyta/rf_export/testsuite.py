from typing import TypedDict

from keyta.rf_export.keywords import RFKeyword
from keyta.rf_export.settings import RFSettings
from keyta.rf_export.testcases import RFTestCase


class RFTestSuite(TypedDict):
    name: str
    settings: RFSettings
    variables: list[tuple[str, list[str]]]
    keywords: list[RFKeyword]
    testcases: list[RFTestCase]
