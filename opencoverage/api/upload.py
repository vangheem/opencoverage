import logging
import os
import zlib
from typing import Optional
from urllib.parse import parse_qs

from starlette.requests import Request
from starlette.responses import PlainTextResponse

from opencoverage import tasks
from opencoverage.clients.scm import get_client

from .app import router

logger = logging.getLogger(__name__)


@router.post("/upload/v4")
async def upload_coverage_v4(request: Request):
    settings = request.app.settings
    path = os.path.join(settings.root_path, "upload-report")
    if path[0] != "/":
        path = "/" + path
    upload_url = str(request.url.replace(path=path))
    scheme = request.headers.get(
        "x-scheme", request.headers.get("x-forwarded-proto", "http")
    )
    if not upload_url.startswith(f"{scheme}://"):
        _, _, url_part = upload_url.partition("://")
        upload_url = f"{scheme}://{url_part}"
    logger.info(f"Redirecting to {upload_url}")
    return PlainTextResponse(f"success\n{upload_url}")


@router.put("/upload-report")
async def upload_report(
    request: Request,
    branch: str,
    commit: str,
    slug: str,
    token: Optional[str] = None,
):
    data = await request.body()
    logger.info(f"Upload body {len(data)}: {request.headers}")

    if request.headers.get("content-type") == "application/x-gzip":
        gzip_worker = zlib.decompressobj(zlib.MAX_WBITS | 16)
        data = gzip_worker.decompress(data) + gzip_worker.flush()
        logger.info(f"decompressed gzip data {len(data)}")

    organization, _, repo = slug.partition("/")

    if token in ("dummy", "-", ".", "y", None):
        installation_id = None
    else:
        installation_id = token

    project = None
    query = parse_qs(request.url.query)
    if query.get("flags"):
        for flag in query["flags"]:
            name, _, value = flag.partition(":")
            if name == "project":
                project = value

    async with get_client(request.app.settings, installation_id) as scm:
        await request.app.db.update_organization(organization, scm.installation_id)

    await request.app.taskrunner.add(
        name="coveragereport",
        config=tasks.CoverageTaskConfig(
            organization=organization,
            repo=repo,
            branch=branch,
            commit=commit,
            project=project,
            installation_id=installation_id,
            data=data,
        ),
    )
    logger.info("Task scheduled")
