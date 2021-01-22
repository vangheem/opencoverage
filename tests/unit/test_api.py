import zlib
from unittest.mock import (
    ANY,
    AsyncMock,
    Mock,
    patch,
)

import pytest
from starlette.datastructures import URL

from opencoverage.api import upload

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def db():
    db = AsyncMock()
    yield db


@pytest.fixture()
def taskrunner():
    tr = AsyncMock()
    yield tr


@pytest.fixture()
def get_client(settings, db, taskrunner, scm):
    with patch("opencoverage.api.upload.get_client", return_value=scm) as mock:
        yield mock


@pytest.fixture()
def req(settings, db, taskrunner, get_client):
    req = AsyncMock()
    req.body.return_value = b"data"
    req.headers = {}
    req.app.settings = settings
    req.app.db = db
    req.app.taskrunner = taskrunner
    yield req


async def test_upload_v4(settings):
    request = Mock()
    settings = Mock()
    request.url = URL("http://foobar.com?foo=bar")
    settings.root_path = "root_path"
    request.app.settings = settings
    resp = await upload.upload_coverage_v4(request)
    _, _, url = resp.body.decode().partition(" ")
    assert url == "http://foobar.com/root_path/upload-report?foo=bar"


class TestUploadReport:
    async def test_upload_report(self, req, db, scm, taskrunner):
        await upload.upload_report(req, branch="branch", commit="commit", slug="org/repo")
        db.update_organization.assert_called_with("org", scm.installation_id)
        taskrunner.add.assert_called_with(name="coveragereport", config=ANY)
        config = taskrunner.add.mock_calls[0].kwargs["config"]
        config.branch == "branch"
        config.commit == "commit"
        config.organization == "org"
        config.data == b"data"

    async def test_upload_report_with_token(
        self, req, db, scm, get_client, settings, taskrunner
    ):
        await upload.upload_report(
            req, branch="branch", commit="commit", slug="org/repo", token="token"
        )
        get_client.assert_called_with(settings, "token")
        taskrunner.add.assert_called_with(name="coveragereport", config=ANY)

    async def test_upload_gzip_report(self, req, db, scm, taskrunner):
        gzip_worker = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
        reports_gzip = gzip_worker.compress(b"data") + gzip_worker.flush()
        req.body.return_value = reports_gzip
        req.headers["content-type"] = "application/x-gzip"

        await upload.upload_report(req, branch="branch", commit="commit", slug="org/repo")
        taskrunner.add.assert_called_with(name="coveragereport", config=ANY)
        config = taskrunner.add.mock_calls[0].kwargs["config"]
        config.branch == "branch"
        config.commit == "commit"
        config.organization == "org"
        config.data == b"data"
