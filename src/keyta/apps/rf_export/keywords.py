from typing import Optional, TypedDict


class RFKeywordCall(TypedDict):
    keyword: str
    args: list[str]
    kwargs: dict[str, str]
    return_value: Optional[str]


class RFKeyword(TypedDict):
    name: str
    doc: str
    args: dict[str, str]
    kwargs: dict[str, str]
    steps: list[RFKeywordCall]
    return_value: Optional[str]
