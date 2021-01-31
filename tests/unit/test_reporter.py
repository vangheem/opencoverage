from unittest.mock import ANY, AsyncMock, patch

import pytest

from opencoverage import models, types
from opencoverage.reporter import CoverageReporter

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def db():
    db = AsyncMock()
    yield db


@pytest.fixture()
def reporter(settings, db, scm):
    yield CoverageReporter(
        settings=settings,
        db=db,
        scm=scm,
        organization="organization",
        repo="repo",
        branch="branch",
        commit="commit",
    )


COVERAGE_DATA = b"""
foobar
<<<<<< network
# path=/path/to/coverage.xml
<?xml version="1.0" ?>
<coverage version="5.3.1" timestamp="1610313969570"
          lines-valid="31160" lines-covered="27879" line-rate="0.8947"
          branches-covered="0" branches-valid="0" branch-rate="0" complexity="0">
	<sources>
		<source>/some/path</source>
	</sources>
	<packages>
		<package name="something" line-rate="0.9112" branch-rate="0" complexity="0">
			<classes>
				<class name="fooobar.py" filename="fooobar.py" complexity="0" line-rate="1" branch-rate="0">
					<methods/>
					<lines>
						<line number="2" hits="1"/>
					</lines>
				</class>
            </classes>
        </package>
    </packages>
</coverage>

<<<<<< EOF
"""  # noqa


async def test_report(reporter, db, scm):
    await reporter(coverage_data=COVERAGE_DATA)
    scm.get_pulls.assert_called_with("organization", "repo", "commit")
    db.save_coverage.assert_called_with(
        organization="organization",
        repo="repo",
        branch="branch",
        commit_hash="commit",
        project=None,
        coverage={
            "version": "5.3.1",
            "timestamp": 1610313969570,
            "lines_covered": 27879,
            "lines_valid": 31160,
            "line_rate": 0.8947,
            "branches_covered": 0,
            "branches_valid": 0,
            "branch_rate": 0.0,
            "complexity": 0,
            "file_coverage": {},
        },
    )


async def test_report_ignores_pull_after_merge(reporter, db, scm):
    scm.get_pulls.return_value = [types.Pull(id=1, base="branch", head="head")]
    await reporter(coverage_data=COVERAGE_DATA)
    scm.get_pulls.assert_called_with("organization", "repo", "commit")
    scm.get_pull_diff.assert_not_called()


async def test_report_get_line_rate(reporter, db, scm):
    coverage = {
        "version": "5.3.1",
        "timestamp": 1610313969570,
        "lines_covered": 27879,
        "lines_valid": 31160,
        "line_rate": 0.8947,
        "branches_covered": 0,
        "branches_valid": 0,
        "branch_rate": 0.0,
        "complexity": 0,
        "file_coverage": {"filename": {"lines": {1: 1}}},
    }
    ddata, rate = reporter.get_line_rate(
        [
            {
                "filename": "filename",
                "lines": [1],
                "line_rate": 1,
                "hits": 1,
                "misses": 1,
            },
            {"filename": "missing", "lines": [1], "line_rate": 1, "hits": 0, "misses": 1},
        ],
        coverage,
    )
    assert ddata == [
        {"filename": "filename", "lines": [1], "line_rate": 1.0, "hits": 1, "misses": 0}
    ]
    assert rate == 1.0


async def test_report_get_line_rate_missing(reporter, db, scm):
    coverage = {
        "version": "5.3.1",
        "timestamp": 1610313969570,
        "lines_covered": 27879,
        "lines_valid": 31160,
        "line_rate": 0.8947,
        "branches_covered": 0,
        "branches_valid": 0,
        "branch_rate": 0.0,
        "complexity": 0,
        "file_coverage": {"filename": {"lines": {1: 0}}},
    }
    ddata, rate = reporter.get_line_rate(
        [
            {
                "filename": "filename",
                "lines": [1],
                "line_rate": 1,
                "hits": 1,
                "misses": 1,
            },
            {"filename": "missing", "lines": [1], "line_rate": 1, "hits": 0, "misses": 1},
        ],
        coverage,
    )
    assert ddata == [
        {"filename": "filename", "lines": [1], "line_rate": 0.0, "hits": 0, "misses": 1}
    ]
    assert rate == 0.0


async def test_report_get_line_rate_missing_files(reporter, db, scm):
    coverage = {
        "version": "5.3.1",
        "timestamp": 1610313969570,
        "lines_covered": 27879,
        "lines_valid": 31160,
        "line_rate": 0.8947,
        "branches_covered": 0,
        "branches_valid": 0,
        "branch_rate": 0.0,
        "complexity": 0,
        "file_coverage": {"filename": {"lines": {}}},
    }
    ddata, rate = reporter.get_line_rate(
        [
            {
                "filename": "filename",
                "lines": [1],
                "line_rate": 1,
                "hits": 1,
                "misses": 1,
            },
            {"filename": "missing", "lines": [1], "line_rate": 1, "hits": 0, "misses": 1},
        ],
        coverage,
    )
    assert ddata == [
        {"filename": "filename", "lines": [1], "line_rate": 1.0, "hits": 0, "misses": 0}
    ]
    assert rate == 1.0


async def test_report_update_pull(reporter, db, scm):
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
    coverage = {
        "version": "5.3.1",
        "timestamp": 1610313969570,
        "lines_covered": 27879,
        "lines_valid": 31160,
        "line_rate": 0.8947,
        "branches_covered": 0,
        "branches_valid": 0,
        "branch_rate": 0.0,
        "complexity": 0,
        "file_coverage": {"filename": {"lines": {1: 1}}},
    }
    await reporter.update_pull(
        types.Pull(id=1, base="base", head="head"), coverage, None, None
    )
    scm.update_comment.assert_called_once()
    db.update_coverage_diff.assert_called_once()
    scm.update_check.assert_called_with(
        "organization", "repo", ANY, running=False, success=True, text=None
    )


async def test_report_update_pull_update_existing_comment(reporter, db, scm):
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
    cdiff = models.CoverageReportPullRequest(comment_id="comment_id")
    db.get_coverage_diff.side_effect = [None, cdiff]
    coverage = {
        "version": "5.3.1",
        "timestamp": 1610313969570,
        "lines_covered": 27879,
        "lines_valid": 31160,
        "line_rate": 0.8947,
        "branches_covered": 0,
        "branches_valid": 0,
        "branch_rate": 0.0,
        "complexity": 0,
        "file_coverage": {"filename": {"lines": {1: 1}}},
    }
    await reporter.update_pull(
        types.Pull(id=1, base="base", head="head"), coverage, None, None
    )

    assert len(db.get_coverage_diff.mock_calls) == 2
    scm.update_comment.assert_called_once()


async def test_report_fix_base_paths(settings, db, scm):
    scm.file_exists.return_value = True

    async def _download_file(*args):
        yield b"""projects:
  ui:
    base_path: app
"""

    scm.download_file = _download_file

    reporter = CoverageReporter(
        settings=settings,
        db=db,
        scm=scm,
        organization="organization",
        repo="repo",
        branch="branch",
        commit="commit",
        project="ui",
    )
    await reporter(
        coverage_data=b"""
foobar.py
<<<<<< network
# path=/path/to/coverage.xml
<?xml version="1.0" ?>
<coverage version="5.3.1" timestamp="1610313969570"
          lines-valid="31160" lines-covered="27879" line-rate="0.8947"
          branches-covered="0" branches-valid="0" branch-rate="0" complexity="0">
	<packages>
		<package name="app" line-rate="0.9112" branch-rate="0" complexity="0">
			<classes>
				<class name="foobar.py" filename="foobar.py" complexity="0" line-rate="1" branch-rate="0">
					<methods/>
					<lines>
						<line number="2" hits="1"/>
					</lines>
				</class>
            </classes>
        </package>
    </packages>
</coverage>

<<<<<< EOF
"""  # noqa
    )
    db.save_coverage.assert_called_with(
        organization="organization",
        repo="repo",
        branch="branch",
        commit_hash="commit",
        project="ui",
        coverage={
            "branch_rate": 0.0,
            "branches_covered": 0,
            "branches_valid": 0,
            "complexity": 0,
            "file_coverage": {
                "app/foobar.py": {
                    "branch_rate": 0.0,
                    "complexity": 0.0,
                    "line_rate": 1.0,
                    "lines": {2: 1},
                }
            },
            "line_rate": 0.8947,
            "lines_covered": 27879,
            "lines_valid": 31160,
            "timestamp": 1610313969570,
            "version": "5.3.1",
        },
    )


async def test_report_no_coverage_file(settings, db, scm):
    scm.file_exists.return_value = False

    reporter = CoverageReporter(
        settings=settings,
        db=db,
        scm=scm,
        organization="organization",
        repo="repo",
        branch="branch",
        commit="commit",
        project="ui",
    )
    await reporter(
        coverage_data=b"""
foobar.py
<<<<<< network
# path=/path/to/coverage.xml
<?xml version="1.0" ?>
<coverage version="5.3.1" timestamp="1610313969570"
          lines-valid="31160" lines-covered="27879" line-rate="0.8947"
          branches-covered="0" branches-valid="0" branch-rate="0" complexity="0">
	<packages>
		<package name="app" line-rate="0.9112" branch-rate="0" complexity="0">
			<classes>
				<class name="foobar.py" filename="foobar.py" complexity="0" line-rate="1" branch-rate="0">
					<methods/>
					<lines>
						<line number="2" hits="1"/>
					</lines>
				</class>
            </classes>
        </package>
    </packages>
</coverage>

<<<<<< EOF
"""  # noqa
    )
    db.save_coverage.assert_called_with(
        organization="organization",
        repo="repo",
        branch="branch",
        commit_hash="commit",
        project="ui",
        coverage={
            "branch_rate": 0.0,
            "branches_covered": 0,
            "branches_valid": 0,
            "complexity": 0,
            "file_coverage": {
                "foobar.py": {
                    "branch_rate": 0.0,
                    "complexity": 0.0,
                    "line_rate": 1.0,
                    "lines": {2: 1},
                }
            },
            "line_rate": 0.8947,
            "lines_covered": 27879,
            "lines_valid": 31160,
            "timestamp": 1610313969570,
            "version": "5.3.1",
        },
    )


async def test_hits_target_diff_coverage(reporter):
    assert reporter.hits_target_diff_coverage(None, None, 0)
    assert reporter.hits_target_diff_coverage(types.CoverageConfiguration(), None, 0)
    assert reporter.hits_target_diff_coverage(
        types.CoverageConfiguration(), types.CoverageConfigurationProject(), 0
    )
    assert reporter.hits_target_diff_coverage(
        types.CoverageConfiguration(diff_target="BADVLAUE"),
        types.CoverageConfigurationProject(),
        0,
    )
    assert reporter.hits_target_diff_coverage(
        types.CoverageConfiguration(diff_target="75%"),
        types.CoverageConfigurationProject(),
        75.1,
    )
    assert not reporter.hits_target_diff_coverage(
        types.CoverageConfiguration(diff_target="75%"),
        types.CoverageConfigurationProject(diff_target="80%"),
        75,
    )
    assert reporter.hits_target_diff_coverage(
        types.CoverageConfiguration(diff_target="75%"),
        types.CoverageConfigurationProject(diff_target="80%"),
        80.1,
    )


async def test_hits_target_coverage(reporter):
    assert reporter.hits_target_coverage(None, None, 0)
    assert reporter.hits_target_coverage(types.CoverageConfiguration(), None, 0)
    assert reporter.hits_target_coverage(
        types.CoverageConfiguration(), types.CoverageConfigurationProject(), 0
    )
    assert reporter.hits_target_coverage(
        types.CoverageConfiguration(target="BADVLAUE"),
        types.CoverageConfigurationProject(),
        0,
    )
    assert reporter.hits_target_coverage(
        types.CoverageConfiguration(target="75%"),
        types.CoverageConfigurationProject(),
        75.1,
    )
    assert not reporter.hits_target_coverage(
        types.CoverageConfiguration(target="75%"),
        types.CoverageConfigurationProject(target="80%"),
        75,
    )
    assert reporter.hits_target_coverage(
        types.CoverageConfiguration(target="75%"),
        types.CoverageConfigurationProject(target="80%"),
        80.1,
    )


async def test_report_update_pull_bad_hit_rate(reporter, db, scm):
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
    coverage = {
        "version": "5.3.1",
        "timestamp": 1610313969570,
        "lines_covered": 27879,
        "lines_valid": 31160,
        "line_rate": 0.8947,
        "branches_covered": 0,
        "branches_valid": 0,
        "branch_rate": 0.0,
        "complexity": 0,
        "file_coverage": {"filename": {"lines": {1: 1}}},
    }
    await reporter.update_pull(
        types.Pull(id=1, base="base", head="head"),
        coverage,
        types.CoverageConfiguration(target="100%"),
        None,
    )
    scm.update_check.assert_called_with(
        "organization",
        "repo",
        ANY,
        running=False,
        success=False,
        text="Misses target line rate with 89.5%",
    )


async def test_report_update_pull_bad_diff_hit_rate(reporter, db, scm):
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
    coverage = {
        "version": "5.3.1",
        "timestamp": 1610313969570,
        "lines_covered": 27879,
        "lines_valid": 31160,
        "line_rate": 0.8947,
        "branches_covered": 0,
        "branches_valid": 0,
        "branch_rate": 0.0,
        "complexity": 0,
        "file_coverage": {"filename": {"lines": {1: 0}}},
    }
    with patch.object(reporter, "get_line_rate", return_value=([], 0.5)):
        await reporter.update_pull(
            types.Pull(id=1, base="base", head="head"),
            coverage,
            types.CoverageConfiguration(diff_target="100%"),
            None,
        )
    scm.update_check.assert_called_with(
        "organization",
        "repo",
        ANY,
        running=False,
        success=False,
        text="Misses target diff line rate with 50.0%",
    )


async def test_coverage_comment(reporter, db, scm):
    text = await reporter.get_coverage_comment(
        [],
        {
            "line_rate": 0.8947,
        },
        0.5,
        types.Pull(id=1, base="base", head="head"),
    )
    assert "50.0%" in text


async def test_coverage_comment_project(reporter, db, scm):
    reporter.project = "foobar"
    text = await reporter.get_coverage_comment(
        [],
        {
            "line_rate": 0.8947,
        },
        0.5,
        types.Pull(id=1, base="base", head="head"),
    )
    assert "`foobar`" in text
