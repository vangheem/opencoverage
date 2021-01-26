from typing import Any, Dict, Optional

from fastapi.responses import StreamingResponse
from starlette.requests import Request
from starlette.responses import JSONResponse

from opencoverage import types
from opencoverage.clients.scm import get_client

from .app import router


@router.get("/{org}/repos")
async def get_repos(org: str, request: Request, cursor: Optional[str] = None):
    db = request.app.db
    result = []
    cursor, repos = await db.get_repos(org, cursor=cursor)
    for repo in repos:
        result.append(
            {
                "name": repo.name,
            }
        )
    return {"cursor": cursor, "result": result}


def _format_report(report):
    return {
        "__type": "CoverageReport",
        "organization": report.organization,
        "repo": report.repo,
        "branch": report.branch,
        "commit_hash": report.commit_hash,
        "lines_valid": report.lines_valid,
        "lines_covered": report.lines_covered,
        "line_rate": report.line_rate,
        "branches_valid": report.branches_valid,
        "branches_covered": report.branches_covered,
        "branch_rate": report.branch_rate,
        "complexity": report.complexity,
        "modification_date": report.modification_date,
        "creation_date": report.creation_date,
    }


@router.get("/{org}/repos/{repo}/commits/{commit}/report")
async def get_report(org: str, repo: str, commit: str, request: Request):
    db = request.app.db
    report = await db.get_report(org, repo, commit)
    if report is None:
        return JSONResponse({}, status_code=404)
    return _format_report(report)


@router.get("/recent-reports")
async def get_recent_reports(
    request: Request, branch: Optional[str] = None, cursor: Optional[str] = None
):
    db = request.app.db
    result = []
    cursor, reports = await db.get_reports(branch=branch, cursor=cursor)
    for report in reports:
        result.append(_format_report(report))
    return {"cursor": cursor, "result": result}


def _format_pr_report(report: types.PRReportResult) -> Dict[str, Any]:
    return {
        "__type": "CoverageReportPullRequest",
        "organization": report["coveragereportpullrequests_organization"],
        "repo": report["coveragereportpullrequests_repo"],
        "branch": report["coveragereportpullrequests_branch"],
        "commit_hash": report["coveragereportpullrequests_commit_hash"],
        "pull": report["coveragereportpullrequests_pull"],
        "pull_diff": report["coveragereportpullrequests_pull_diff"],
        "line_rate": report["coveragereportpullrequests_line_rate"],
        "modification_date": report["coveragereportpullrequests_modification_date"],
        "creation_date": report["coveragereportpullrequests_creation_date"],
        "coverage": {
            "lines_valid": report["coveragereports_lines_valid"],
            "line_rate": report["coveragereports_line_rate"],
            "lines_covered": report["coveragereports_lines_covered"],
            "branches_valid": report["coveragereports_branches_valid"],
            "branches_covered": report["coveragereports_branches_covered"],
            "branch_rate": report["coveragereports_branch_rate"],
            "complexity": report["coveragereports_complexity"],
            "modification_date": report["coveragereports_modification_date"],
            "creation_date": report["coveragereports_creation_date"],
        },
    }


@router.get("/recent-pr-reports")
async def get_recent_pr_reports(request: Request, cursor: Optional[str] = None):
    db = request.app.db
    result = []
    cursor, reports = await db.get_pr_reports(cursor=cursor)
    for report in reports:
        result.append(_format_pr_report(report))
    return {"cursor": cursor, "result": result}


@router.get("/{org}/repos/{repo}/reports")
async def get_reports(
    org: str, repo: str, request: Request, cursor: Optional[str] = None
):
    db = request.app.db
    result = []
    cursor, reports = await db.get_reports(org, repo, cursor=cursor)
    for report in reports:
        result.append(_format_report(report))
    return {"cursor": cursor, "result": result}


@router.get("/{org}/repos/{repo}/pulls/{pull}/{commit}/report")
async def get_pr_report(org: str, repo: str, pull: str, commit: str, request: Request):
    db = request.app.db
    _, reports = await db.get_pr_reports(
        organization=org, repo=repo, pull=pull, commit=commit
    )
    if len(reports) > 0:
        return _format_pr_report(reports[0])
    return JSONResponse({"reason": "notFound"}, status_code=404)


@router.get("/{org}/repos/{repo}/pulls")
async def get_pulls(org: str, repo: str, request: Request, cursor: Optional[str] = None):
    db = request.app.db
    result = []
    cursor, pulls = await db.get_pulls(org, repo, cursor=cursor)
    for pr in pulls:
        result.append({"id": pr.id, "base": pr.base, "head": pr.head})
    return {"cursor": cursor, "result": result}


@router.get("/{org}/repos/{repo}/commits/{commit}/files")
async def get_files(
    org: str, repo: str, commit: str, request: Request, cursor: Optional[str] = None
):
    db = request.app.db
    cursor, files = await db.get_report_files(org, repo, commit, cursor=cursor)
    return {
        "cursor": cursor,
        "result": [
            {"filename": fi["filename"], "line_rate": fi["line_rate"]} for fi in files
        ],
    }


@router.get("/{org}/repos/{repo}/commits/{commit}/file")
async def get_file(org: str, repo: str, commit: str, request: Request, filename: str):
    db = request.app.db
    fi = await db.get_report_file(org, repo, commit, filename)
    if fi is None:
        return JSONResponse({"reason": "fileNotFound"}, status_code=404)
    return {
        "__type": "ReportFile",
        "filename": fi.filename,
        "organization": fi.organization,
        "repo": fi.repo,
        "branch": fi.branch,
        "commit_hash": fi.commit_hash,
        "lines": fi.lines,
        "line_rate": fi.line_rate,
        "branch_rate": fi.branch_rate,
        "complexity": fi.complexity,
        "creation_date": fi.creation_date,
        "modification_date": fi.modification_date,
    }


@router.get("/{org}/repos/{repo}/commits/{commit}/download")
async def download_file(
    org: str, repo: str, commit: str, request: Request, filename: str
):
    organization = await request.app.db.get_organization(org)
    if organization is None:
        return JSONResponse({"reason": "orgNotFound"}, status_code=404)

    async with get_client(request.app.settings, organization.installation_id) as scm:
        if not await scm.file_exists(org, repo, commit, filename):
            return JSONResponse({"reason": "fileNotFound"}, status_code=404)
        return StreamingResponse(scm.download_file(org, repo, commit, filename))
