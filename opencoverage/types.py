from typing import (
    Dict,
    List,
    Optional,
    TypedDict,
)

import pydantic


class FileCoverageData(TypedDict):
    line_rate: float
    branch_rate: float
    complexity: float
    lines: Dict[int, int]


class CoverageData(TypedDict):
    base_path: Optional[str]
    version: str
    timestamp: int
    lines_valid: int
    lines_covered: int
    line_rate: float
    branches_covered: int
    branches_valid: int
    branch_rate: float
    complexity: float

    file_coverage: Dict[str, FileCoverageData]


class DiffCoverage(TypedDict):
    filename: str
    lines: List[int]
    line_rate: float
    hits: int
    misses: int


class Pull(pydantic.BaseModel):
    id: int
    base: str
    head: str
