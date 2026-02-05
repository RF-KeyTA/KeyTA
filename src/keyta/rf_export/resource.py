from typing import TypedDict

from keyta.rf_export.keywords import RFKeyword
from keyta.rf_export.settings import RFSettings


class RFResource(TypedDict):
    settings: RFSettings
    keywords: list[RFKeyword]
