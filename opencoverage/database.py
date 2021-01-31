from datetime import datetime
from typing import (
    List,
    Optional,
    Tuple,
    TypedDict,
    cast,
)

import sqlalchemy.exc
import sqlalchemy.orm.exc
from asyncom.om import OMDatabase
from databases import DatabaseURL

from . import models, types
from .models import (
    ROOT_PROJECT,
    Branch,
    Commit,
    CoverageRecord,
    CoverageReport,
    CoverageReportPullRequest,
    Organization,
    PullRequest,
    Repo,
    Task,
)
from .settings import Settings


class ReportFilesType(TypedDict):
    filename: str
    line_rate: float


class Database:
    def __init__(self, settings: Settings):
        models.init(settings.dsn)
        self.db = OMDatabase(DatabaseURL(settings.dsn))

    async def initialize(self):
        if not self.db.is_connected:
            await self.db.connect()

    async def finalize(self):
        if self.db.is_connected:
            try:
                await self.db.disconnect()
            except RuntimeError:  # pragma: no cover
                # loop closing
                ...

    async def _ensure_ob(self, model, **data):
        filters = []
        for key, value in data.items():
            filters.append(getattr(model, key) == value)
        try:
            return await self.db.query(model).filter(*filters).one()
        except sqlalchemy.orm.exc.NoResultFound:
            ob = model(
                creation_date=datetime.utcnow(),
                modification_date=datetime.utcnow(),
                **data,
            )
            await self.db.add(ob)
            return ob

    async def _paged_results(
        self,
        query,
        cursor_type,
        limit: int = 10,
        cursor: Optional[str] = None,
        reverse: bool = False,
    ) -> Tuple[Optional[str], List[models.Base]]:
        if cursor is not None:
            query = query.filter(cursor_type > cursor)
        if reverse:
            query = query.order_by(cursor_type.desc()).limit(limit)
        else:
            query = query.order_by(cursor_type).limit(limit)
        results = await query.all()
        cursor = None
        if len(results) == limit:
            cursor = getattr(results[-1], cursor_type.key)
        return cursor, results

    async def get_repos(
        self, organization: str, limit: int = 10, cursor: Optional[str] = None
    ) -> Tuple[Optional[str], List[Repo]]:
        return await self._paged_results(
            self.db.query(Repo).filter(Repo.organization == organization),
            Repo.name,
            limit=limit,
            cursor=cursor,
        )

    async def get_reports(
        self,
        organization: Optional[str] = None,
        repo: Optional[str] = None,
        branch: Optional[str] = None,
        project: Optional[str] = None,
        limit: int = 10,
        cursor: Optional[str] = None,
    ) -> Tuple[str, List[CoverageReport]]:
        query = self.db.query(CoverageReport)
        if organization is not None:
            query = query.filter(CoverageReport.organization == organization)
        if repo is not None:
            query = query.filter(CoverageReport.repo == repo)
        if branch is not None:
            query = query.filter(CoverageReport.branch == branch)
        if project is not None:
            query = query.filter(CoverageReport.project == project)
        return cast(
            Tuple[str, List[CoverageReport]],
            await self._paged_results(
                query,
                CoverageReport.modification_date,
                limit=limit,
                cursor=cursor,
                reverse=True,
            ),
        )

    async def get_pr_reports(
        self,
        organization: Optional[str] = None,
        repo: Optional[str] = None,
        pull: Optional[int] = None,
        commit: Optional[str] = None,
        project: Optional[str] = None,
        limit: int = 10,
        cursor: Optional[str] = None,
    ) -> Tuple[str, List[types.PRReportResult]]:
        query = self.db.query(
            [CoverageReportPullRequest, CoverageReport],
            mapper_factory=lambda q, context: lambda v: v,
        )
        if organization is not None:
            query = query.filter(CoverageReportPullRequest.organization == organization)
        if repo is not None:
            query = query.filter(CoverageReportPullRequest.repo == repo)
        if pull is not None:
            query = query.filter(CoverageReportPullRequest.pull == int(pull))
        if commit is not None:
            query = query.filter(CoverageReportPullRequest.commit_hash == commit)
        if project is not None:
            query = query.filter(CoverageReportPullRequest.project == project)
        query = query.outerjoin(
            CoverageReport,
            CoverageReportPullRequest.commit_hash == CoverageReport.commit_hash,
        ).filter(
            CoverageReportPullRequest.project == CoverageReport.project,
        )

        if cursor is not None:
            query = query.filter(CoverageReportPullRequest.modification_date > cursor)
        query = query.order_by(CoverageReportPullRequest.modification_date.desc()).limit(
            limit
        )

        results = await query.all()
        cursor_result = None
        if len(results) == limit:
            cursor_result = results[-1]["coveragereportpullrequests_modification_date"]
        return cast(Tuple[str, List[types.PRReportResult]], (cursor_result, results))

    async def get_report(
        self, organization: str, repo: str, commit: str, project: Optional[str] = None
    ) -> Optional[CoverageReport]:
        try:
            return (
                await self.db.query(CoverageReport)
                .filter(
                    CoverageReport.organization == organization,
                    CoverageReport.repo == repo,
                    CoverageReport.commit_hash == commit,
                    CoverageReport.project == (project or ROOT_PROJECT),
                )
                .one()
            )
        except sqlalchemy.orm.exc.NoResultFound:
            return None

    async def get_pulls(
        self, organization: str, repo: str, limit: int = 10, cursor: Optional[str] = None
    ) -> Tuple[str, List[PullRequest]]:
        return cast(
            Tuple[str, List[PullRequest]],
            await self._paged_results(
                self.db.query(PullRequest).filter(
                    PullRequest.organization == organization, PullRequest.repo == repo
                ),
                PullRequest.id,
                limit=limit,
                cursor=cursor,
                reverse=True,
            ),
        )

    async def get_report_files(
        self,
        organization: str,
        repo: str,
        commit_hash: str,
        project: Optional[str] = None,
        limit: int = 500,
        cursor: Optional[str] = None,
    ) -> Tuple[Optional[str], List[ReportFilesType]]:
        query = self.db.query(
            [
                CoverageRecord.filename.label("filename"),
                CoverageRecord.line_rate.label("line_rate"),
            ],
            mapper_factory=lambda q, context: lambda v: v,
        ).filter(
            CoverageRecord.organization == organization,
            CoverageRecord.repo == repo,
            CoverageRecord.commit_hash == commit_hash,
            CoverageRecord.project == (project or ROOT_PROJECT),
        )
        if cursor is not None:
            query = query.filter(CoverageRecord.filename > cursor)
        query = query.order_by(CoverageRecord.filename).limit(limit)
        results: List[ReportFilesType] = await query.all()
        cursor = None
        if len(results) == limit:
            cursor = results[-1]["filename"]
        return cursor, results

    async def get_report_file(
        self,
        organization: str,
        repo: str,
        commit_hash: str,
        filename: str,
        project: Optional[str] = None,
    ) -> Optional[CoverageRecord]:
        try:
            return (
                await self.db.query(CoverageRecord)
                .filter(
                    CoverageRecord.organization == organization,
                    CoverageRecord.repo == repo,
                    CoverageRecord.commit_hash == commit_hash,
                    CoverageRecord.filename == filename,
                    CoverageRecord.project == (project or ROOT_PROJECT),
                )
                .one()
            )
        except sqlalchemy.orm.exc.NoResultFound:
            return None

    def _update_coverage_data(
        self,
        report,
        coverage: types.CoverageData,
    ) -> None:
        for name in (
            "lines_valid",
            "lines_covered",
            "line_rate",
            "branches_valid",
            "branches_covered",
            "branch_rate",
            "complexity",
        ):
            setattr(report, name, coverage[name])  # type: ignore
        report.modification_date = datetime.utcnow()

    async def get_coverage_diff(
        self,
        *,
        organization: str,
        repo: str,
        branch: str,
        pull: types.Pull,
        commit_hash: Optional[str] = None,
        project: Optional[str] = None,
    ) -> Optional[CoverageReportPullRequest]:
        filters = [
            CoverageReportPullRequest.organization == organization,
            CoverageReportPullRequest.branch == branch,
            CoverageReportPullRequest.repo == repo,
            CoverageReportPullRequest.pull == pull.id,
            CoverageReportPullRequest.project == (project or ROOT_PROJECT),
        ]
        if commit_hash is not None:
            filters.append(CoverageReportPullRequest.commit_hash == commit_hash)
        try:
            return await self.db.query(CoverageReportPullRequest).filter(*filters).one()
        except sqlalchemy.orm.exc.NoResultFound:
            return None

    async def update_coverage_diff(self, *, report: CoverageReportPullRequest) -> None:
        await self.db.update(report)

    async def create_coverage_diff(
        self,
        *,
        organization: str,
        repo: str,
        branch: str,
        commit_hash: str,
        project: Optional[str],
        pull: types.Pull,
        pull_diff: List[types.DiffCoverage],
        check_id: str,
        comment_id: str,
        line_rate: float,
    ) -> None:
        if project is None:
            project = ROOT_PROJECT

        await self._ensure_ob(
            Branch, name=pull.base, organization=organization, repo=repo
        )
        await self._ensure_ob(
            Branch, name=pull.head, organization=organization, repo=repo
        )
        await self._ensure_ob(
            PullRequest,
            organization=organization,
            repo=repo,
            id=pull.id,
            base=pull.base,
            head=pull.head,
        )

        report = CoverageReportPullRequest(
            organization=organization,
            branch=branch,
            repo=repo,
            commit_hash=commit_hash,
            project=project,
            pull=pull.id,
            pull_diff=pull_diff,
            check_id=check_id,
            comment_id=comment_id,
            line_rate=line_rate,
            creation_date=datetime.utcnow(),
            modification_date=datetime.utcnow(),
        )
        await self.db.add(report)

    async def update_organization(self, name: str, install_id: str):
        try:
            org = (
                await self.db.query(Organization)
                .filter(
                    Organization.name == name,
                )
                .one()
            )
            org.installation_id = install_id
            await self.db.update(org)
        except sqlalchemy.orm.exc.NoResultFound:
            org = Organization(name=name, installation_id=install_id)
            await self.db.add(org)

    async def get_organization(self, name: str) -> Optional[Organization]:
        try:
            return (
                await self.db.query(Organization)
                .filter(
                    Organization.name == name,
                )
                .one()
            )
        except sqlalchemy.orm.exc.NoResultFound:
            return None

    async def save_coverage(
        self,
        *,
        organization: str,
        repo: str,
        branch: str,
        commit_hash: str,
        coverage: types.CoverageData,
        project: Optional[str] = ROOT_PROJECT,
    ) -> None:
        if project is None:
            project = ROOT_PROJECT

        await self._ensure_ob(Repo, name=repo, organization=organization)
        await self._ensure_ob(Branch, name=branch, organization=organization, repo=repo)
        await self._ensure_ob(
            Commit, branch=branch, organization=organization, repo=repo, hash=commit_hash
        )

        try:
            report = (
                await self.db.query(CoverageReport)
                .filter(
                    CoverageReport.organization == organization,
                    CoverageReport.branch == branch,
                    CoverageReport.repo == repo,
                    CoverageReport.commit_hash == commit_hash,
                    CoverageReport.project == project,
                )
                .one()
            )
            self._update_coverage_data(report, coverage)
            await self.db.update(report)
        except sqlalchemy.orm.exc.NoResultFound:
            report = CoverageReport(
                organization=organization,
                branch=branch,
                repo=repo,
                commit_hash=commit_hash,
                creation_date=datetime.utcnow(),
                project=project,
            )
            self._update_coverage_data(report, coverage)
            await self.db.add(report)

        async with self.db.transaction():
            await self.db.query(CoverageRecord).filter(
                CoverageRecord.branch == branch,
                CoverageRecord.organization == organization,
                CoverageRecord.repo == repo,
                CoverageRecord.commit_hash == commit_hash,
                CoverageRecord.project == project,
            ).delete()
            for filename, source in coverage["file_coverage"].items():
                await self.db.add(
                    CoverageRecord(
                        branch=branch,
                        organization=organization,
                        repo=repo,
                        commit_hash=commit_hash,
                        filename=filename,
                        project=project,
                        lines=source["lines"],
                        line_rate=source["line_rate"],
                        branch_rate=source["branch_rate"],
                        complexity=source["complexity"],
                        creation_date=datetime.utcnow(),
                        modification_date=datetime.utcnow(),
                    )
                )

    async def add_task(self, *, name: str, data: bytes, status: str):
        await self.db.add(
            Task(
                name=name,
                data=data,
                status=status,
                creation_date=datetime.utcnow(),
                modification_date=datetime.utcnow(),
            )
        )

    async def update_task(self, task):
        task.modification_date = datetime.utcnow()
        await self.db.update(task)

    async def remove_task(self, task: Task):
        await self.db.delete(task)

    async def get_task(self) -> Optional[Task]:
        try:
            return (
                await self.db.query(
                    Task,
                )
                .filter(Task.status != "error")
                .order_by(Task.creation_date)
                .limit(1)
                .with_for_update(skip_locked=True)
                .one()
            )
        except sqlalchemy.orm.exc.NoResultFound:
            return None
