from typing import Optional, TypedDict

from keyta.rf_export.keywords import RFKeywordCall


class RFTestCase(TypedDict):
    name: str
    doc: Optional[str]
    setup: Optional[RFKeywordCall]
    variables: list[tuple[str, list[str]]]
    steps: list[RFKeywordCall]
    teardown: Optional[RFKeywordCall]
