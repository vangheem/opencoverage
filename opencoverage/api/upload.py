import zlib
from typing import Optional

from starlette.requests import Request
from starlette.responses import PlainTextResponse

from opencoverage import tasks
from opencoverage.clients.scm import get_client

from .app import router
import os


@router.post("/upload/v4")
async def upload_coverage_v4(request: Request):
    settings = request.app.settings
    path = os.path.join(settings.root_path, "upload-report")
    if path[0] != "/":
        path = "/" + path
    upload_url = str(request.url.replace(path=path))
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

    if token in ("dummy", "-", ".", "y", None):
        installation_id = None
    else:
        installation_id = token

    async with get_client(request.app.settings, installation_id) as scm:
        await request.app.db.update_organization(organization, scm.installation_id)

    await request.app.taskrunner.add(
        name="coveragereport",
        config=tasks.CoverageTaskConfig(
            organization=organization,
            repo=repo,
            branch=branch,
            commit=commit,
            installation_id=installation_id,
            data=data,
        ),
    )
