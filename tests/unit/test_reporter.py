from unittest.mock import ANY, AsyncMock

import pytest

from opencoverage import types
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


async def test_report(reporter, db, scm):
    await reporter(
        coverage_data=b"""
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
    )
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
        types.Pull(id=1, base="base", head="head"),
        coverage,
    )
    scm.update_comment.assert_called_once()
    db.update_coverage_diff.assert_called_once()
    scm.update_check.assert_called_with(
        "organization", "repo", ANY, running=False, success=True
    )


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
