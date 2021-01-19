from unittest.mock import AsyncMock

import pytest

from opencoverage.settings import Settings


@pytest.fixture()
def pg_dsn():
    yield "postgresql://opencoverage:secret@localhost:5432/opencoverage?sslmode=disable"


@pytest.fixture()
def scm():
    mock = AsyncMock()
    yield mock


@pytest.fixture()
def settings(pg_dsn):
    settings = Settings(dsn=pg_dsn, scm="dummy")
    yield settings
