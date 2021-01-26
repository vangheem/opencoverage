from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import sqlalchemy.orm.exc

from opencoverage import models, types
from opencoverage.database import Database

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def raw():
    db = AsyncMock()
    db.query = MagicMock(return_value=db)
    db.filter = MagicMock(return_value=db)
    db.order_by = MagicMock(return_value=db)
    db.limit = MagicMock(return_value=db)

    txn = AsyncMock()
    db.transaction = MagicMock(return_value=txn)

    yield db


@pytest.fixture()
def db(raw, settings):
    with patch("opencoverage.database.OMDatabase", return_value=raw):
        yield Database(settings)


class TestLifecycle:
    async def test_initialize(self, db, raw):
        raw.is_connected = False
        await db.initialize()
        raw.connect.assert_called_once()

    async def test_initialize_already_connected(self, db, raw):
        raw.is_connected = True
        await db.initialize()
        raw.connect.assert_not_called()

    async def test_finalize(self, db, raw):
        raw.is_connected = True
        await db.finalize()
        raw.disconnect.assert_called_once()

    async def test_finalize_not_connected(self, db, raw):
        raw.is_connected = False
        await db.finalize()
        raw.disconnect.assert_not_called()

    async def test_finalize_runtime_error(self, db, raw):
        raw.is_connected = True
        raw.disconnect.side_effect = RuntimeError
        await db.finalize()
        raw.disconnect.assert_called_once()


class TestGetRepos:
    async def test_get_repos(self, db, raw):
        repo = models.Repo()
        raw.all.return_value = [repo]
        cursor, results = await db.get_repos("organization")
        assert cursor is None
        assert results == [repo]
        raw.query.assert_called_with(models.Repo)
        raw.filter.assert_called_once()
        raw.order_by.assert_called_with(models.Repo.name)
        raw.limit.assert_called_with(10)
        raw.all.assert_called_once()

    async def test_get_repos_cursor(self, db, raw):
        repo1 = models.Repo(name="1")
        raw.all.return_value = [repo1]
        cursor, results = await db.get_repos("organization", limit=1)
        assert cursor == "1"
        assert results == [repo1]
        raw.query.assert_called_with(models.Repo)
        raw.filter.assert_called_once()
        raw.order_by.assert_called_with(models.Repo.name)
        raw.limit.assert_called_with(1)
        raw.all.assert_called_once()

    async def test_get_repos_by_cursor(self, db, raw):
        repo2 = models.Repo(name="2")
        raw.all.return_value = [repo2]
        cursor, results = await db.get_repos("organization", limit=1, cursor="1")
        assert cursor == "2"
        assert results == [repo2]
        raw.query.assert_called_with(models.Repo)
        assert len(raw.filter.mock_calls) == 2
        raw.order_by.assert_called_with(models.Repo.name)
        raw.limit.assert_called_with(1)
        raw.all.assert_called_once()


class TestGetReports:
    async def test_get_reports(self, db, raw):
        report = models.CoverageReport()
        raw.all.return_value = [report]
        cursor, results = await db.get_reports("organization", "repo", "branch")
        assert cursor is None
        assert results == [report]
        raw.query.assert_called_with(models.CoverageReport)
        assert len(raw.filter.mock_calls) == 3
        raw.order_by.assert_called_once()
        raw.limit.assert_called_with(10)
        raw.all.assert_called_once()


class TestGetReportFiles:
    async def test_get_report_files(self, db, raw):
        record = {"filename": "filename"}
        raw.all.return_value = [record]
        cursor, results = await db.get_report_files(
            "organization", "repo", "commit_hash", 1, "cursor"
        )
        assert cursor == "filename"
        assert results == [record]
        raw.query.assert_called_once()
        assert len(raw.filter.mock_calls) == 2
        raw.order_by.assert_called_once()
        raw.limit.assert_called_with(1)
        raw.all.assert_called_once()


class TestCoverageDiff:
    async def test_update_coverage_diff(self, db, raw):
        report = models.CoverageReportPullRequest()
        await db.update_coverage_diff(report=report)
        raw.update.assert_called_with(report)


class TestOrganization:
    async def test_update_organization(self, db, raw):
        org = models.Organization()
        raw.one.return_value = org
        await db.update_organization("name", "install_id")
        assert org.installation_id == "install_id"
        raw.update.assert_called_with(org)

    async def test_update_organization_new(self, db, raw):
        raw.one.side_effect = sqlalchemy.orm.exc.NoResultFound
        await db.update_organization("name", "install_id")
        raw.add.assert_called_once()


class TestSaveCoverage:
    async def test_update_organization(self, db, raw):
        await db.save_coverage(
            organization="organization",
            repo="repo",
            branch="branch",
            commit_hash="commit_hash",
            coverage={
                "lines_valid": "lines_valid",
                "lines_covered": "lines_covered",
                "line_rate": "line_rate",
                "branches_valid": "branches_valid",
                "branches_covered": "branches_covered",
                "branch_rate": "branch_rate",
                "complexity": "complexity",
                "file_coverage": {},
            },
        )
        raw.update.assert_called_once()


class TestTasks:
    async def test_update_task(self, db, raw):
        task = models.Task()
        await db.update_task(task)
        assert task.modification_date
        raw.update.assert_called_with(task)
