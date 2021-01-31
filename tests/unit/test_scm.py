import os
from datetime import datetime, timedelta, timezone
from unittest.mock import (
    AsyncMock,
    MagicMock,
    Mock,
    patch,
)

import pytest

from opencoverage.clients import scm
from tests import utils

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def _clear():
    scm.github._token_cache.clear()
    scm.github._private_key_cache.clear()


def test_get_client_unsupported():
    settings = Mock()
    settings.scm = "missing"
    with pytest.raises(TypeError):
        scm.get_client(settings, None)


class TestGithub:
    @pytest.fixture()
    async def client(self, settings):
        settings.github_app_pem_file = os.path.join(utils.DATA_DIR, "test.pem")
        cli = scm.Github(settings, None)
        yield cli
        await cli.close()

    @pytest.fixture()
    def response(self):
        res = AsyncMock()
        res.status = 200
        res.json.return_value = {"foo": "bar"}
        res.text.return_value = '{"foo": "bar"}'
        yield res

    @pytest.fixture()
    def req(self, response):
        req = AsyncMock()
        req.__aenter__.return_value = response
        yield req

    @pytest.fixture()
    def session(self, client, req):
        session = MagicMock()

        session.post.return_value = req
        session.patch.return_value = req
        session.put.return_value = req
        session.get.return_value = req

        with patch("opencoverage.clients.scm.github.aiohttp_client", session):
            yield session

    @pytest.fixture()
    def token(self, client):
        with patch.object(client, "get_access_token", return_value="token"):
            yield "token"

    def test_get_client_github_missing_pem(self):
        settings = Mock()
        settings.scm = "github"
        settings.github_app_pem_file = None
        with pytest.raises(TypeError):
            assert scm.get_client(settings, None)

    async def test_get_client(self, client):
        assert client

    async def test_get_access_token(self, client, session, response):
        response.status = 201
        response.json.return_value = scm.github.GithubAccessData(
            token="token",
            expires_at=datetime.utcnow().replace(tzinfo=timezone.utc)
            + timedelta(hours=1),
            permissions={},
            repository_selection="repository_selection",
        ).dict()
        token = await client.get_access_token()
        assert token == "token"

    async def test_get_access_token_failure(self, client, session, response):
        response.status = 401
        response.json.return_value = {"error": "error"}
        with pytest.raises(scm.github.APIException):
            await client.get_access_token()

    async def test_get_access_token_cache(self, client, session, response):
        response.status = 201
        response.json.return_value = scm.github.GithubAccessData(
            token="token",
            expires_at=datetime.utcnow().replace(tzinfo=timezone.utc)
            + timedelta(hours=1),
            permissions={},
            repository_selection="repository_selection",
        ).dict()
        token = await client.get_access_token()
        assert token == "token"
        calls = len(session.post.mock_calls)

        assert await client.get_access_token() == "token"
        assert len(session.post.mock_calls) == calls

    async def test_get_pulls_missing(self, client, session, response, token):
        response.status = 422
        pulls = await client.get_pulls("org", "repo", "commit_hash")
        assert len(pulls) == 0

    async def test_get_pulls_auth_error(self, client, session, response, token):
        response.status = 401
        with pytest.raises(scm.github.AuthorizationException):
            await client.get_pulls("org", "repo", "commit_hash")

    async def test_get_pull_diff_auth_error(self, client, session, response, token):
        response.status = 401
        with pytest.raises(scm.github.AuthorizationException):
            await client.get_pull_diff("org", "repo", "id")

    async def test_create_check(self, client, session, response, token):
        response.status = 201
        check = scm.github.GithubCheck(
            id=123,
            status="created",
            started_at=datetime.utcnow(),
            name="name",
            head_sha="head_sha",
        )
        response.json.return_value = check.dict()
        assert await client.create_check("org", "repo", "commit") == "123"

    async def test_create_check_auth_error(self, client, session, response, token):
        response.status = 401
        with pytest.raises(scm.github.AuthorizationException):
            await client.create_check("org", "repo", "commit")

    async def test_update_check(self, client, session, response, token):
        await client.update_check("org", "repo", "check_id", text="foobar")
        assert session.patch.mock_calls[0].kwargs["json"] == {
            "status": "completed",
            "conclusion": "failure",
            "output": {
                "summary": "Recording and checking coverage data",
                "title": "foobar",
            },
        }

    async def test_update_check_success(self, client, session, response, token):
        await client.update_check("org", "repo", "check_id", running=True, success=True)
        assert session.patch.mock_calls[0].kwargs["json"] == {
            "status": "in_progress",
            "conclusion": "success",
            "output": {
                "summary": "Recording and checking coverage data",
                "title": "Successful",
            },
        }

    async def test_update_check_auth_error(self, client, session, response, token):
        response.status = 401
        with pytest.raises(scm.github.APIException):
            await client.update_check("org", "repo", "check_id")

    async def test_create_comment(self, client, session, response, token):
        response.status = 201
        comment = scm.github.GithubComment(id=123, body="text")
        response.json.return_value = comment.dict()
        assert await client.create_comment("org", "repo", "pull_id", "text") == "123"

    async def test_create_comment_auth_error(self, client, session, response, token):
        response.status = 401
        with pytest.raises(scm.github.APIException):
            await client.create_comment("org", "repo", "pull_id", "text")

    async def test_update_comment(self, client, session, response, token):
        response.status = 200
        await client.update_comment("org", "repo", "123", "text")

    async def test_update_comment_auth_error(self, client, session, response, token):
        response.status = 401
        with pytest.raises(scm.github.APIException):
            await client.update_comment("org", "repo", "123", "text")

    async def test_download_file_401(self, client, session, response, token):
        response.status = 401
        with pytest.raises(scm.github.AuthorizationException):
            async for chunk in client.download_file("org", "repo", "commit", "filename"):
                ...

    async def test_download_file_404(self, client, session, response, token):
        response.status = 404
        with pytest.raises(scm.github.NotFoundException):
            async for chunk in client.download_file("org", "repo", "commit", "filename"):
                ...

    async def test_file_exists(self, client, session, response, token):
        response.status = 200
        assert await client.file_exists("org", "repo", "commit", "filename")

    async def test_not_file_exists(self, client, session, response, token):
        response.status = 404
        assert not await client.file_exists("org", "repo", "commit", "filename")

    async def test_file_exists_authz(self, client, session, response, token):
        response.status = 401
        with pytest.raises(scm.github.AuthorizationException):
            assert not await client.file_exists("org", "repo", "commit", "filename")

    async def test_app_installation_does_not_validate(self, client, session, response):
        response.status = 404
        with pytest.raises(scm.github.AuthorizationException):
            await client.validate()

    async def test_app_installation_does_not_validate_perms(
        self, client, session, response
    ):
        response.status = 200
        response.json.return_value = scm.github.GithubInstallation(
            app_id=1,
            app_slug="app_slug",
            created_at="created_at",
            id=1,
            permissions={"foo": "write"},
        ).dict()
        with pytest.raises(scm.github.InstallationException):
            await client.validate()
