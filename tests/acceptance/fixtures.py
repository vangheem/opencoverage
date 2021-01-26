import asyncio

import pytest
import sqlalchemy as sa
import sqlalchemy.exc
from async_asgi_testclient import TestClient

from opencoverage import models
from opencoverage.api.app import HTTPApplication
from opencoverage.models import Task


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
def db(app):
    yield app.db


class TasksChecker:
    def __init__(self, app):
        self.app = app

    async def wait(self):
        while await self.app.db.db.query(Task).filter(Task.status != "error").count() > 0:
            await asyncio.sleep(0.1)


@pytest.fixture()
def tasks(app):
    yield TasksChecker(app)


@pytest.fixture()
async def http_client(app):
    async with TestClient(app) as client:
        yield client
