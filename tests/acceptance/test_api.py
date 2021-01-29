from unittest.mock import patch

import pytest

from opencoverage import types
from tests.utils import add_coverage, read_data

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def scm_app(scm):
    with patch("opencoverage.api.api.get_client", return_value=scm), patch(
        "opencoverage.api.upload.get_client", return_value=scm
    ), patch("opencoverage.tasks.get_client", return_value=scm):
        yield


@pytest.fixture()
async def coverage(settings, db, scm):
    await add_coverage(
        settings, db, scm, "plone", "guillotina", "master", "123", "guillotina.cov"
    )


async def test_upload(http_client, scm):
    resp = await http_client.put(
        "/upload-report",
        query_string={
            "slug": "plone/guillotina",
            "branch": "master",
            "commit": "38432y",
            "flags": "foo:bar",
        },
        data=read_data("guillotina.cov"),
    )
    assert resp.status_code == 200


async def test_upload_with_project(http_client, scm):
    resp = await http_client.put(
        "/upload-report",
        query_string={
            "slug": "plone/guillotina",
            "branch": "master",
            "commit": "38432y",
            "flags": "project:api",
        },
        data=read_data("guillotina.cov"),
    )
    assert resp.status_code == 200


async def test_upload_against_pr(http_client, scm, tasks):
    scm.get_pulls.return_value = [types.Pull(head="test-changes", base="master", id="1")]
    scm.get_pull_diff.return_value = """diff --git a/guillotina/addons.py b/guillotina/addons.py
index 8ad9304b..de0e1d25 100644
--- a/guillotina/addons.py
+++ b/guillotina/addons.py
@@ -29,6 +29,7 @@ async def install(container, addon):
         await install(container, dependency)
     await apply_coroutine(handler.install, container, request)
     registry = task_vars.registry.get()
+    registry
     config = registry.for_interface(IAddons)
     config["enabled"] |= {addon}

"""
    scm.create_check.return_value = "check"
    scm.create_comment.return_value = "comment"

    params = {
        "slug": "vangheem/guillotina",
        "branch": "test-changes",
        "commit": "59cc8f62c5e0d13a685bb3d388e8cb10669aebec",
    }
    resp = await http_client.put(
        "/upload-report",
        query_string=params,
        data=read_data("guillotina.pr"),
    )
    assert resp.status_code == 200

    await tasks.wait()

    resp = await http_client.get("/vangheem/repos/guillotina/pulls")
    assert resp.status_code == 200
    assert len(resp.json()["result"]) == 1

    resp = await http_client.get(
        "/vangheem/repos/guillotina/pulls/1/59cc8f62c5e0d13a685bb3d388e8cb10669aebec/report"
    )
    assert resp.status_code == 200
    assert resp.json()["commit_hash"] == "59cc8f62c5e0d13a685bb3d388e8cb10669aebec"

    resp = await http_client.get("/recent-pr-reports")
    assert resp.status_code == 200
    assert len(resp.json()["result"]) == 1


async def test_get_pr_report_404(http_client):
    resp = await http_client.get("/vangheem/repos/guillotina/pulls/1/123/report")
    assert resp.status_code == 404


async def test_get_repos(http_client, app, coverage):
    resp = await http_client.get("/plone/repos")
    assert resp.status_code == 200
    assert resp.json() == {"cursor": None, "result": [{"name": "guillotina"}]}


async def test_get_report(http_client, app, coverage):
    resp = await http_client.get("/plone/repos/guillotina/commits/123/report")
    assert resp.status_code == 200
    data = resp.json()
    assert data["branch"] == "master"


async def test_get_report_404(http_client, app):
    resp = await http_client.get("/plone/repos/guillotina/commits/missing/report")
    assert resp.status_code == 404


async def test_add_lcov_report(http_client, app, settings, db, scm):
    await add_coverage(settings, db, scm, "plone", "guillotina", "master", "123", "lcov")
    resp = await http_client.get("/recent-reports")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["result"]) == 1


async def test_get_recent_reports(http_client, app, settings, db, scm):
    await add_coverage(
        settings, db, scm, "plone", "guillotina", "master", "123", "guillotina.cov"
    )
    await add_coverage(
        settings, db, scm, "plone", "guillotina", "master", "1234", "guillotina.cov"
    )
    resp = await http_client.get("/recent-reports")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["result"]) == 2


async def test_get_reports(http_client, app, settings, db, scm):
    await add_coverage(
        settings, db, scm, "plone", "guillotina", "master", "123", "guillotina.cov"
    )
    await add_coverage(
        settings, db, scm, "plone", "guillotina", "master", "1234", "guillotina.cov"
    )
    resp = await http_client.get("/plone/repos/guillotina/reports")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["result"]) == 2


async def test_get_files(http_client, app, coverage):
    resp = await http_client.get("/plone/repos/guillotina/commits/123/files")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["result"]) == 373


async def test_get_file(http_client, app, coverage):
    resp = await http_client.get(
        "/plone/repos/guillotina/commits/123/file",
        query_string={"filename": "guillotina/content.py"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "guillotina/content.py"
    assert len(data["lines"]) == 547

    resp = await http_client.get(
        "/plone/repos/guillotina/commits/123/file",
        query_string={"filename": "foobar.py"},
    )
    assert resp.status_code == 404


async def test_get_badge(http_client, app, settings, db, scm):
    await add_coverage(
        settings, db, scm, "plone", "guillotina", "master", "123", "guillotina.cov"
    )
    await add_coverage(
        settings, db, scm, "plone", "guillotina", "master", "1234", "guillotina.cov"
    )
    resp = await http_client.get("/plone/repos/guillotina/badge.svg")
    assert resp.status_code == 200
    assert "<svg" in resp.content.decode()


async def test_download_file(http_client, db, scm):
    await db.update_organization("plone", "123")
    scm.file_exists.return_value = True

    async def _download_file(*args):
        yield b"data"

    scm.download_file = _download_file
    resp = await http_client.get(
        "/plone/repos/guillotina/commits/123/download",
        query_string={"filename": "foobar.py"},
    )
    assert resp.status_code == 200


async def test_download_file_org_not_found(http_client):
    resp = await http_client.get(
        "/plone/repos/guillotina/commits/123/download",
        query_string={"filename": "foobar.py"},
    )
    assert resp.status_code == 404
    assert resp.json()["reason"] == "orgNotFound"


async def test_download_file_not_found(http_client, db, scm):
    await db.update_organization("plone", "123")
    scm.file_exists.return_value = False

    resp = await http_client.get(
        "/plone/repos/guillotina/commits/123/download",
        query_string={"filename": "foobar.py"},
    )
    assert resp.status_code == 404
    assert resp.json()["reason"] == "fileNotFound"
