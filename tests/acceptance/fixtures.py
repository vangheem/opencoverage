import pytest
import sqlalchemy as sa
import sqlalchemy.exc
from async_asgi_testclient import TestClient

from opencoverage import models
from opencoverage.api.app import HTTPApplication


@pytest.fixture()
def bootstrap(pg_dsn):
    # clear out before starting tests so we can test bootstrapping as well
    engine = sa.create_engine(pg_dsn)

    for model in reversed(models.MODELS):
        try:
            model.__table__.drop(engine)
        except sqlalchemy.exc.ProgrammingError:
            ...

    models.init(pg_dsn)
    yield


@pytest.fixture()
def app(settings, bootstrap):
    yield HTTPApplication(settings)


@pytest.fixture()
async def http_client(app):
    async with TestClient(app) as client:
        yield client
