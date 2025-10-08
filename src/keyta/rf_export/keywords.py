from typing import Optional, TypedDict


class RFKeywordCall(TypedDict):
    condition: str
    keyword: str
    params: list[str]
    return_values: list[str]
    table_var: Optional[str]
    table_columns: list[str]


class RFKeyword(TypedDict):
    name: str
    doc: str
    args: list[str]
    kwargs: dict[str, str]
    steps: list[RFKeywordCall]
    return_values: list[str]
