from typing import Optional, TypedDict

from keyta.rf_export.keywords import RFKeywordCall


class RFTestCase(TypedDict):
    name: str
    doc: Optional[str]
    steps: list[RFKeywordCall]
