from unittest.mock import patch

import pytest

from opencoverage import types
from tests.utils import add_coverage, read_data

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def scm_app(scm):
    with patch("opencoverage.api.app.scm.get_client", return_value=scm):
        yield


async def test_upload(http_client, scm):
    scm.get_pulls.return_value = []
    resp = await http_client.put(
        "/upload-report",
        query_string={"slug": "plone/guillotina", "branch": "master", "commit": "38432y"},
        data=read_data("guillotina.cov"),
    )
    assert resp.status_code == 200


async def test_upload_against_pr(http_client, scm):
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

    resp = await http_client.get("/vangheem/repos/guillotina/pulls")
    assert resp.status_code == 200
    assert len(resp.json()["result"]) == 1


async def test_get_repos(http_client, app):
    await add_coverage(app.db, "plone", "guillotina", "master", "123", "guillotina.cov")
    resp = await http_client.get("/plone/repos")
    assert resp.status_code == 200
    assert resp.json() == {"cursor": None, "result": [{"name": "guillotina"}]}


async def test_get_report(http_client, app):
    await add_coverage(app.db, "plone", "guillotina", "master", "123", "guillotina.cov")
    resp = await http_client.get("/plone/repos/guillotina/commits/123/report")
    assert resp.status_code == 200
    data = resp.json()
    assert data["branch"] == "master"


async def test_get_reports(http_client, app):
    await add_coverage(app.db, "plone", "guillotina", "master", "123", "guillotina.cov")
    await add_coverage(app.db, "plone", "guillotina", "master", "1234", "guillotina.cov")
    resp = await http_client.get("/plone/repos/guillotina/reports")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["result"]) == 2


async def test_get_files(http_client, app):
    await add_coverage(app.db, "plone", "guillotina", "master", "123", "guillotina.cov")
    resp = await http_client.get("/plone/repos/guillotina/commits/123/files")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["result"]) == 373


async def test_get_file(http_client, app):
    await add_coverage(app.db, "plone", "guillotina", "master", "123", "guillotina.cov")
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
