import abc
import traceback
from typing import AsyncIterator, List, Optional, Type

import aiohttp

from opencoverage.settings import Settings
from opencoverage.types import Pull


class SCMClient(abc.ABC):
    installation_id: str

    def __init__(self, settings: Settings, installation_id: Optional[str]):
        self.settings = settings
        self._session = None

    async def close(self):
        if self._session is not None:
            await self._session.close()

    @property
    def session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    @abc.abstractmethod
    async def get_pulls(self, org: str, repo: str, commit_hash: str) -> List[Pull]:
        ...

    @abc.abstractmethod
    async def get_pull_diff(self, org: str, repo: str, id: int) -> str:
        ...

    @abc.abstractmethod
    async def create_check(self, org: str, repo: str, commit: str) -> str:
        ...

    @abc.abstractmethod
    async def update_check(
        self,
        org: str,
        repo: str,
        check_id: str,
        running: bool = False,
        success: bool = False,
    ) -> None:
        ...

    @abc.abstractmethod
    async def create_comment(self, org: str, repo: str, pull_id: int, text: str) -> str:
        ...

    @abc.abstractmethod
    async def update_comment(
        self, org: str, repo: str, comment_id: str, text: str
    ) -> None:
        ...

    @abc.abstractmethod
    async def download_file(
        self, org: str, repo: str, commit: str, filename: str
    ) -> AsyncIterator[bytes]:  # pragma: no cover
        yield b""

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[Exception]],
        exc_value: Optional[Exception],
        exc_traceback: Optional[traceback.StackSummary],
    ):
        await self.close()