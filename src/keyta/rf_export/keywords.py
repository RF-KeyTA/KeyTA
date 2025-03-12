from typing import Optional, TypedDict


class RFKeywordCall(TypedDict):
    condition: str
    keyword: str
    args: list[str]
    kwargs: dict[str, str]
    return_values: list[str]
    list_var: Optional[str]


class RFKeyword(TypedDict):
    name: str
    doc: str
    args: list[str]
    kwargs: dict[str, str]
    steps: list[RFKeywordCall]
    return_value: Optional[str]
