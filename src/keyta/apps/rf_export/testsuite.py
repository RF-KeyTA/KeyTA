from typing import TypedDict

from apps.rf_export.keywords import RFKeyword
from apps.rf_export.settings import RFSettings
from apps.rf_export.testcases import RFTestCase


class RFTestSuite(TypedDict):
    name: str
    settings: RFSettings
    keywords: list[RFKeyword]
    testcases: list[RFTestCase]
