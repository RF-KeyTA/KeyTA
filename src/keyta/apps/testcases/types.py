from typing import TypedDict, Optional, Literal


class ParamData(TypedDict):
    """
    ParamData
    index: int
    name: str
    value: str
    """
    index: int
    name: str
    value: str


class ParamMetadata(TypedDict):
    """
    ParamMetadata
    index: int
    pk: int
    """
    index: int
    pk: int


class StepData(TypedDict):
    """
    StepData
    index: int
    name: str
    params: list[ParamData]|list[list]
    """
    index: int
    name: str
    params: list[ParamData]|list[list]


class StepMetadata(TypedDict):
    """
    StepMetadata
    index: int
    params: list[ParamMetadata]
    pk: int
    type: Literal['DICT', 'LIST']
    """
    index: int
    params: list[ParamMetadata]
    pk: int
    to_keyword_pk: int
    type: Literal['DICT', 'LIST']


class StepParameterValues(TypedDict):
    """
    StepParameterValues
    params: dict[pk: int, value: str]
    table: Optional[tuple[name: str, rows: list]]
    """
    params: dict[int, str]
    table: Optional[tuple[str, list[list[str]]]]


class TestStepsData(TypedDict):
    """
    TestStepsData
    steps: list[StepData]
    metadata: list[StepMetadata]
    """
    steps: list[StepData]
    metadata: list[StepMetadata]
