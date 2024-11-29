from typing import TypedDict

from apps.rf_export.keywords import RFKeyword
from apps.rf_export.settings import RFSettings


class RFResource(TypedDict):
    settings: RFSettings
    keywords: list[RFKeyword]
