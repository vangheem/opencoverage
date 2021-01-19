from typing import Optional

from starlette.requests import Request
from starlette.responses import PlainTextResponse

from opencoverage.reporter import CoverageReporter

from .app import router


@router.post("/upload/v4")
async def upload_coverage_v4(request: Request):
    upload_url = str(request.url.replace(path="/upload-report"))
    return PlainTextResponse(f"success {upload_url}")


@router.put("/upload-report")
async def upload_report(
    request: Request, branch: str, commit: str, slug: str, token: Optional[str] = None
):
    data = await request.body()
    organization, _, repo = slug.partition("/")

    reporter = CoverageReporter(
        settings=request.app.settings,
        db=request.app.db,
        scm=request.app.scm,
        organization=organization,
        repo=repo,
        branch=branch,
        commit=commit,
    )
    await reporter(coverage_data=data)
