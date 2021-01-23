import asyncio
import logging
import pickle
import traceback
from typing import (
    Any,
    Dict,
    Optional,
    Tuple,
    Type,
)

import pydantic

from opencoverage.database import Database

from .models import Task
from .settings import Settings

logger = logging.getLogger(__name__)
_registered: Dict[str, Tuple[Any, Type[pydantic.BaseModel]]] = {}


def register(name: str, func: Any, config: Type[pydantic.BaseModel]):
    _registered[name] = (func, config)


class InvalidTaskException(Exception):
    ...


class TaskRunner:
    """
    The purpose of tasks are to store task data in the database and
    to be able to run jobs based on that task data
    """

    check_interval = 0.5
    consume_task: Optional[asyncio.Task]

    def __init__(self, settings: Settings, db: Database):
        self.settings = settings
        self.db = db
        self.consume_task = None
        self._consuming_tasks = False

    async def add(self, *, name: str, config: pydantic.BaseModel) -> None:
        if name not in _registered:
            raise InvalidTaskException(f"Task is not registered: {name}")
        _, config_type = _registered[name]
        if not isinstance(config, config_type):
            raise InvalidTaskException(f"Invalid task config: {name}: {config}")
        await self.db.add_task(name=name, data=pickle.dumps(config), status="scheduled")

    async def start_consuming(self) -> None:
        self._consuming_tasks = True
        self.consume_task = asyncio.create_task(self.run_tasks())

    async def stop_consuming(self) -> None:
        self._consuming_tasks = False
        # give it some time to finish
        if self.consume_task is not None:
            await asyncio.wait([self.consume_task], timeout=5)
            if not self.consume_task.done():  # pragma: no cover
                self.consume_task.cancel()
                # wait more for cleanup
                await asyncio.wait([self.consume_task], timeout=1)
        self.consume_task = None

    async def run_tasks(self) -> None:
        while self._consuming_tasks:
            try:
                await self._run_tasks()
                await asyncio.sleep(self.check_interval)
            except (RuntimeError, asyncio.CancelledError):  # pragma: no cover
                return
            except Exception:
                logger.exception(
                    "Unhandled error running tasks, trying again", exc_info=True
                )
                await asyncio.sleep(1)

    async def _run_tasks(self) -> None:
        error = False
        task = None
        try:
            async with self.db.db.transaction():
                task = await self.db.get_task()
                if task is None:
                    return
                logger.info(f"Running task: {task.name}: {task.id}")
                await self.run_task(task)
                await self.db.remove_task(task)
        except Exception:
            error = True
            logger.exception("Error running task")
        else:
            logger.info(f"Finished task: {task.name}: {task.id}")
        if error and task is not None:
            logger.error(f"Marking task in error: {task.name}: {task.id}")
            # on error, put task in error status
            task.status = "error"
            task.info = traceback.format_exc()
            # remove old bad data that caused the error?
            await self.db.update_task(task)

    async def run_task(self, task: Task) -> None:
        func, _ = _registered[task.name]
        config = pickle.loads(task.data)
        await func(self, config)
        logger.info(f"Finished task: {task.name}: {task.id}")
