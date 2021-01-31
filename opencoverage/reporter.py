import os
from io import StringIO
from typing import List, Optional, Tuple

import yaml

from opencoverage.models import ROOT_PROJECT
from opencoverage.settings import Settings

from . import types
from .clients import SCMClient
from .database import Database
from .parser import parse_diff, parse_raw_coverage_data
from .utils import run_async


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
        project: Optional[str] = None,
    ):
        self.settings = settings
        self.db = db
        self.scm = scm
        self.organization = organization
        self.repo = repo
        self.branch = branch
        self.commit = commit
        self.project = project

    async def __call__(
        self,
        *,
        coverage_data: bytes,
    ) -> None:
        coverage = await run_async(parse_raw_coverage_data, coverage_data)

        config = await self.get_coverage_configuration()
        project_config = None
        if self.project is not None and config is not None:
            # check to see if we need to fix paths in report
            if (
                config is not None
                and config.projects is not None
                and self.project in config.projects
            ):
                project_config = config.projects[self.project]
                if project_config.base_path is not None:
                    # fix paths in coverage report
                    for filepath in [f for f in coverage["file_coverage"].keys()]:
                        new_filepath = os.path.join(project_config.base_path, filepath)
                        coverage["file_coverage"][new_filepath] = coverage[
                            "file_coverage"
                        ][filepath]
                        del coverage["file_coverage"][filepath]

        await self.db.save_coverage(
            organization=self.organization,
            repo=self.repo,
            branch=self.branch,
            commit_hash=self.commit,
            coverage=coverage,
            project=self.project,
        )

        pulls = await self.scm.get_pulls(self.organization, self.repo, self.commit)
        for pull in pulls:
            if self.branch == pull.base:
                continue
            await self.update_pull(pull, coverage, config, project_config)

    def hits_target_diff_coverage(
        self,
        config: types.CoverageConfiguration,
        project_config: types.CoverageConfigurationProject,
        rate: float,
    ) -> bool:
        diff_target = None
        # check coverage targets
        if config is not None:
            diff_target = config.diff_target
            if project_config is not None:
                if project_config.diff_target is not None:
                    diff_target = project_config.diff_target

        if diff_target is not None:
            try:
                target = float(diff_target.strip("%"))
                return rate >= target
            except ValueError:
                ...
        return True

    def hits_target_coverage(
        self,
        config: types.CoverageConfiguration,
        project_config: types.CoverageConfigurationProject,
        rate: float,
    ) -> bool:
        target = None
        # check coverage targets
        if config is not None:
            target = config.target
            if project_config is not None:
                if project_config.target is not None:
                    target = project_config.target

        if target is not None:
            try:
                target = float(target.strip("%"))
                return rate >= target
            except ValueError:
                ...
        return True

    async def get_coverage_configuration(self) -> Optional[types.CoverageConfiguration]:
        if await self.scm.file_exists(
            self.organization, self.repo, self.commit, "cov.yaml"
        ):
            data = b""
            async for chunk in self.scm.download_file(
                self.organization, self.repo, self.commit, "cov.yaml"
            ):
                data += chunk
            text = data.decode("utf-8")
            data = yaml.safe_load(StringIO(text))
            return types.CoverageConfiguration.parse_obj(data)
        return None

    @property
    def report_url(self) -> str:
        return f"{self.settings.public_url}/{self.organization}/repos/{self.repo}/commits/{self.commit}/report"

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

        project_text = ""
        if self.project not in (ROOT_PROJECT, None):
            project_text = f"`{self.project}`"

        diff_url = f"{self.settings.public_url}/{self.organization}/repos/{self.repo}/pulls/{pull.id}/{self.commit}/report"  # noqa
        return f"""
## Coverage Report {project_text}

Overall coverage: *{(100 * coverage["line_rate"]):.1f}%*
[Coverage report]({self.report_url})


```diff
@@           Coverage Diff            @@
========================================
- Coverage    {(diff_line_rate * 100):.1f}%
========================================
+ Hits        {hits}
- Misses      {misses}

```
[Diff coverage report]({diff_url})
"""  # noqa

    def get_line_rate(
        self, diff_data: List[types.DiffCoverage], coverage: types.CoverageData
    ) -> Tuple[List[types.DiffCoverage], float]:
        total = 0
        covered = 0
        covered_diff_data = []
        for ddata in diff_data:
            try:
                lines = coverage["file_coverage"][ddata["filename"]]["lines"]
            except KeyError:
                # if it isn't in the file coverage report, we don't care about it
                continue

            file_total = 0
            file_covered = 0
            ddata["hits"] = ddata["misses"] = 0
            for line_no, hits in lines.items():
                if line_no in ddata["lines"]:
                    file_total += 1
                    if hits:
                        file_covered += 1
                        ddata["hits"] += 1
                    else:
                        ddata["misses"] += 1

            if file_total > 0:
                ddata["line_rate"] = file_covered / file_total
            else:
                ddata["line_rate"] = 1.0
            total += file_total
            covered += file_covered
            covered_diff_data.append(ddata)

        if total > 0:
            return covered_diff_data, covered / total
        return covered_diff_data, 1.0

    async def update_pull(
        self,
        pull: types.Pull,
        coverage: types.CoverageData,
        config: types.CoverageConfiguration,
        project_config: types.CoverageConfigurationProject,
    ):
        diff = await self.scm.get_pull_diff(self.organization, self.repo, pull.id)
        diff_data = await run_async(parse_diff, diff)
        diff_data, diff_line_rate = self.get_line_rate(diff_data, coverage)

        check_id = await self.scm.create_check(
            self.organization, self.repo, self.commit, details_url=self.report_url
        )

        coverage_diff = await self.db.get_coverage_diff(
            organization=self.organization,
            repo=self.repo,
            branch=self.branch,
            commit_hash=self.commit,
            project=self.project,
            pull=pull,
        )
        text = await self.get_coverage_comment(diff_data, coverage, diff_line_rate, pull)

        if coverage_diff is None:
            # check to see if there is already a comment on the PR with a different diff
            # with different commit hash
            coverage_diff = await self.db.get_coverage_diff(
                organization=self.organization,
                repo=self.repo,
                branch=self.branch,
                project=self.project,
                pull=pull,
            )
            if coverage_diff is None:
                comment_id = await self.scm.create_comment(
                    self.organization, self.repo, pull.id, text
                )
            else:
                comment_id = coverage_diff.comment_id
                await self.scm.update_comment(
                    self.organization, self.repo, coverage_diff.comment_id, text
                )

            await self.db.create_coverage_diff(
                organization=self.organization,
                repo=self.repo,
                branch=self.branch,
                commit_hash=self.commit,
                project=self.project,
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
        check_text = None
        if not self.hits_target_coverage(
            config, project_config, 100 * coverage["line_rate"]
        ):
            success = False
            check_text = (
                f'Does not hit configured line rate: {100 * coverage["line_rate"]}%'
            )
        elif not self.hits_diff_target_coverage(
            config, project_config, 100 * diff_line_rate
        ):
            success = False
            check_text = (
                f"Does not hit configured diff line rate: {100 * diff_line_rate}%"
            )
        await self.scm.update_check(
            self.organization,
            self.repo,
            check_id,
            running=False,
            success=success,
            text=check_text,
        )
