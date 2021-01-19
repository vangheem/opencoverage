from opencoverage.settings import Settings
from typing import List
from . import types
from .clients import SCMClient
from .database import Database
from .parser import parse_diff, parse_raw_coverage_data


class CoverageReporter:
    def __init__(
        self,
        *,
        settings: Settings,
        db: Database,
        scm: SCMClient,
        organization: str,
        repo: str,
        branch: str,
        commit: str,
    ):
        self.settings = settings
        self.db = db
        self.scm = scm
        self.organization = organization
        self.repo = repo
        self.branch = branch
        self.commit = commit

    async def __call__(
        self,
        *,
        coverage_data: bytes,
    ) -> None:
        coverage = parse_raw_coverage_data(coverage_data)

        await self.db.save_coverage(
            organization=self.organization,
            repo=self.repo,
            branch=self.branch,
            commit_hash=self.commit,
            coverage=coverage,
        )

        pulls = await self.scm.get_pulls(self.organization, self.repo, self.commit)
        for pull in pulls:
            await self.update_pull(pull, coverage)

    async def get_coverage_comment(
        self,
        diff_data: List[types.DiffCoverage],
        coverage: types.CoverageData,
        diff_line_rate: float,
        pull: types.Pull,
    ) -> str:
        hits = 0
        misses = 0
        for ddata in diff_data:
            hits += ddata["hits"]
            misses += ddata["misses"]

        return f"""
## Coverage Report

Overall coverage: *{coverage["line_rate"]}%*
Coverage report: {self.settings.public_url}/report/{self.organization}/{self.repo}/{self.branch}/{self.commit}


```diff
@@           Coverage Diff            @@
========================================
- Coverage    {diff_line_rate}%
========================================
+ Hits        {hits}
- Misses      {misses}

```
Diff coverage report: {self.settings.public_url}/report/{self.organization}/{self.repo}/{self.branch}/{self.commit}/{pull.id}
"""  # noqa

    def get_line_rate(
        self, diff_data: List[types.DiffCoverage], coverage: types.CoverageData
    ) -> float:
        total = 0
        covered = 0
        for ddata in diff_data:
            try:
                lines = coverage["file_coverage"][ddata["filename"]]["lines"]
            except KeyError:
                ddata["line_rate"] = 0.0
                ddata["hits"] = 0
                ddata["misses"] = len(ddata["lines"])
                total += len(ddata["lines"])
                continue

            file_total = len(ddata["lines"])
            file_covered = 0
            ddata["hits"] = ddata["misses"] = 0
            for lnum in ddata["lines"]:
                if lines.get(lnum, 0):
                    file_covered += 1
                    ddata["hits"] += 1
                else:
                    ddata["misses"] += 1

            ddata["line_rate"] = file_covered / file_total
            total += file_total
            covered += file_covered

        return covered / total

    async def update_pull(self, pull: types.Pull, coverage: types.CoverageData):
        diff = await self.scm.get_pull_diff(self.organization, self.repo, pull.id)
        diff_data = parse_diff(diff)
        diff_line_rate = self.get_line_rate(diff_data, coverage)

        check_id = await self.scm.create_check(self.organization, self.repo, self.commit)

        coverage_diff = await self.db.get_coverage_diff(
            organization=self.organization,
            repo=self.repo,
            branch=self.branch,
            commit_hash=self.commit,
            pull=pull,
        )
        text = await self.get_coverage_comment(diff_data, coverage, diff_line_rate, pull)

        if coverage_diff is None:
            comment_id = await self.scm.create_comment(
                self.organization, self.repo, pull.id, text
            )
            await self.db.create_coverage_diff(
                organization=self.organization,
                repo=self.repo,
                branch=self.branch,
                commit_hash=self.commit,
                pull=pull,
                pull_diff=diff_data,
                check_id=check_id,
                comment_id=comment_id,
                line_rate=diff_line_rate,
            )
        else:
            await self.scm.update_comment(
                self.organization, self.repo, coverage_diff.comment_id, text
            )
            coverage_diff.pull_diff = diff_data
            coverage_diff.line_rate = diff_line_rate  # type: ignore
            await self.db.update_coverage_diff(report=coverage_diff)

        success = True
        await self.scm.update_check(
            self.organization, self.repo, check_id, running=False, success=success
        )
