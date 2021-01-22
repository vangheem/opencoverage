from typing import Optional

import pydantic

from . import taskrunner
from .clients.scm import get_client
from .reporter import CoverageReporter


class CoverageTaskConfig(pydantic.BaseModel):
    organization: str
    repo: str
    branch: str
    commit: str
    installation_id: Optional[str]
    data: bytes


async def run_coverage_report(
    runner: taskrunner.TaskRunner, config: CoverageTaskConfig
) -> None:
    async with get_client(runner.settings, config.installation_id) as scm:
        reporter = CoverageReporter(
            settings=runner.settings,
            db=runner.db,
            scm=scm,
            organization=config.organization,
            repo=config.repo,
            branch=config.branch,
            commit=config.commit,
        )
        await reporter(coverage_data=config.data)


taskrunner.register("coveragereport", run_coverage_report, CoverageTaskConfig)
