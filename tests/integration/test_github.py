import pytest

from opencoverage.clients.scm import get_client
from opencoverage.settings import Settings

pytestmark = pytest.mark.asyncio


@pytest.fixture()
async def github():
    async with get_client(Settings(scm="github"), None) as client:
        yield client


async def test_get_pulls(github):
    pulls = await github.get_pulls(
        "vangheem", "guillotina", "d375e051a9aeb3e931b4fc679d7e79f6cf12d505"
    )
    assert len(pulls) == 1
    assert pulls[0].base == "master"
    assert pulls[0].head == "test-changes"


async def test_get_pull_diff(github):
    diff = await github.get_pull_diff("vangheem", "guillotina", 1)
    assert "diff --git a/guillotina/addons.py b/guillotina/addons.py" in diff


async def test_download_file(github):
    data = b""
    async for chunk in github.download_file(
        "vangheem",
        "guillotina",
        "d375e051a9aeb3e931b4fc679d7e79f6cf12d505",
        "guillotina/addons.py",
    ):
        data += chunk
    assert "async def uninstall(container, addon)" in data.decode("utf-8")
