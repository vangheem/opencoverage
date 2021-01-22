import zlib
from typing import Optional

from starlette.requests import Request
from starlette.responses import PlainTextResponse

from opencoverage.clients.scm import get_client
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

    if request.headers.get("content-type") == "application/x-gzip":
        gzip_worker = zlib.decompressobj(zlib.MAX_WBITS | 16)
        data = gzip_worker.decompress(data) + gzip_worker.flush()

    organization, _, repo = slug.partition("/")

    if token in ("dummy", "-", ".", "y"):
        installation_id = None
    else:
        installation_id = token

    async with get_client(request.app.settings, installation_id) as scm:
        await request.app.db.update_organization(organization, scm.installation_id)

        reporter = CoverageReporter(
            settings=request.app.settings,
            db=request.app.db,
            scm=scm,
            organization=organization,
            repo=repo,
            branch=branch,
            commit=commit,
        )
        await reporter(coverage_data=data)
