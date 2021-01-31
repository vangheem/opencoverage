from datetime import datetime
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


class PRReportResult(TypedDict):
    coveragereportpullrequests_organization: str
    coveragereportpullrequests_repo: str
    coveragereportpullrequests_branch: str
    coveragereportpullrequests_commit_hash: str
    coveragereportpullrequests_project: Optional[str]
    coveragereportpullrequests_pull: str
    coveragereportpullrequests_pull_diff: str
    coveragereportpullrequests_line_rate: float
    coveragereportpullrequests_modification_date: datetime
    coveragereportpullrequests_creation_date: datetime
    coveragereports_lines_valid: int
    coveragereports_line_rate: float
    coveragereports_lines_covered: int
    coveragereports_branches_valid: int
    coveragereports_branches_covered: int
    coveragereports_branch_rate: float
    coveragereports_complexity: float
    coveragereports_modification_date: datetime
    coveragereports_creation_date: datetime


class CoverageConfigurationProject(pydantic.BaseModel):
    base_path: Optional[str] = None
    target: Optional[str] = None


class CoverageConfiguration(pydantic.BaseModel):
    projects: Optional[Dict[str, CoverageConfigurationProject]] = None
