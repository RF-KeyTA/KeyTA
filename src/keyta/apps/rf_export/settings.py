from typing import Optional, TypedDict

from apps.rf_export.keywords import RFKeywordCall


class RFLibraryImport(TypedDict):
    library: str
    kwargs: dict[str, str]


class RFResourceImport(TypedDict):
    resource: str


class RFSettings(TypedDict):
    library_imports: list[RFLibraryImport]
    resource_imports: list[RFResourceImport]
    suite_setup: Optional[RFKeywordCall]
    suite_teardown: Optional[RFKeywordCall]
    test_setup: Optional[RFKeywordCall]
    test_teardown: Optional[RFKeywordCall]
