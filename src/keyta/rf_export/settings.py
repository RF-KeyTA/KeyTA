from typing import Optional, TypedDict

from keyta.rf_export.keywords import RFKeywordCall


class RFLibraryImport(TypedDict):
    library: str
    kwargs: dict[str, str]


class RFResourceImport(TypedDict):
    resource: str


class RFSettings(TypedDict):
    library_imports: dict[int, RFLibraryImport]
    resource_imports: dict[int, RFResourceImport]
    suite_setup: Optional[RFKeywordCall]
    suite_teardown: Optional[RFKeywordCall]
