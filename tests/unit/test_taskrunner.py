import asyncio
import pickle
from unittest.mock import (
    ANY,
    AsyncMock,
    MagicMock,
    Mock,
    patch,
)

import pydantic
import pytest

from opencoverage import taskrunner, tasks

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def db():
    db = AsyncMock()
    raw_db = AsyncMock()
    txn = AsyncMock()
    raw_db.transaction = MagicMock(return_value=txn)
    db.db = raw_db
    db.get_task.return_value = None
    yield db


@pytest.fixture()
def runner(db):
    yield taskrunner.TaskRunner(None, db)


class FooType(pydantic.BaseModel):
    foo: str


class TestAddTask:
    async def test_add_unregistered_task(self, runner):
        with pytest.raises(taskrunner.InvalidTaskException):
            await runner.add(name="invalid", config=None)

    async def test_add_invalid_config_type(self, runner):
        with pytest.raises(taskrunner.InvalidTaskException):
            await runner.add(name="coveragereport", config=FooType(foo="bar"))

    async def test_add_task(self, db, runner):
        config = tasks.CoverageTaskConfig(
            organization="organization",
            repo="repo",
            branch="branch",
            commit="commit",
            installation_id="installation_id",
            data=b"data",
        )
        await runner.add(name="coveragereport", config=config)
        db.add_task.assert_called_with(
            name="coveragereport", data=pickle.dumps(config), status="scheduled"
        )


class TestConsume:
    async def test_consume(self, db, runner):
        await runner.start_consuming()
        await runner.stop_consuming()
        assert runner.consume_task is None

    async def test_stop_consuming_without_start(self, db, runner):
        await runner.stop_consuming()
        assert runner.consume_task is None

    async def test_run_tasks_retries_on_error(self, runner):
        with patch("opencoverage.taskrunner.logger") as logger, patch.object(
            runner, "_run_tasks", side_effect=Exception()
        ):
            await runner.start_consuming()
            await asyncio.sleep(0.01)
            await runner.stop_consuming()
            logger.exception.assert_called()

    async def test_run_tasks_handles_exceptions(self, runner, db):
        task = Mock()
        db.get_task.return_value = task
        with patch.object(runner, "run_task", side_effect=Exception()):
            await runner.start_consuming()
            await asyncio.sleep(0.01)
            await runner.stop_consuming()
            db.update_task.assert_called_with(task)
            assert task.status == "error"

    async def test_run_task(self, runner, db):

        task_func = AsyncMock()
        task = Mock()
        task.name = "test"
        task.data = pickle.dumps(FooType(foo="foo"))

        with patch.dict(
            taskrunner._registered, {"test": (task_func, FooType)}, clear=True
        ):
            await runner.run_task(task)
            task_func.assert_called_with(runner, ANY)
