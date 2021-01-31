import os
from unittest.mock import AsyncMock

import aiohttp_client
import pytest

from opencoverage.settings import Settings


@pytest.fixture()
def pg_dsn():
    if "DSN" in os.environ:
        yield os.environ["DSN"]
    else:
        yield "postgresql://opencoverage:secret@localhost:5432/opencoverage?sslmode=disable"


@pytest.fixture()
def scm():
    mock = AsyncMock()
    mock.__aenter__.return_value = mock
    mock.installation_id = "1234"
    mock.get_pulls.return_value = []
    mock.file_exists.return_value = False
    yield mock


@pytest.fixture()
def settings(pg_dsn):
    settings = Settings(dsn=pg_dsn, scm="dummy")
    yield settings


@pytest.fixture(autouse=True)
def clear_aiohttp_sessions(event_loop):
    event_loop.run_until_complete(aiohttp_client.close())
