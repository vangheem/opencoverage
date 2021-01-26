import os
from unittest.mock import AsyncMock

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
    yield mock


@pytest.fixture()
def settings(pg_dsn):
    settings = Settings(dsn=pg_dsn, scm="dummy")
    yield settings
