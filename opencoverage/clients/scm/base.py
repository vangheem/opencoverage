import abc
import traceback
from typing import (
    AsyncIterator,
    List,
    Optional,
    Type,
)

from opencoverage.settings import Settings
from opencoverage.types import Pull


class SCMClient(abc.ABC):
    installation_id: str

    def __init__(self, settings: Settings, installation_id: Optional[str]):
        self.settings = settings

    async def close(self):  # pragma: no cover
        ...

    @abc.abstractmethod
    async def get_pulls(
        self, org: str, repo: str, commit_hash: str
    ) -> List[Pull]:  # pragma: no cover
        ...

    @abc.abstractmethod
    async def get_pull_diff(
        self, org: str, repo: str, id: int
    ) -> str:  # pragma: no cover
        ...

    @abc.abstractmethod
    async def create_check(
        self, org: str, repo: str, commit: str, details_url: Optional[str] = None
    ) -> str:  # pragma: no cover
        ...

    @abc.abstractmethod
    async def update_check(
        self,
        org: str,
        repo: str,
        check_id: str,
        running: bool = False,
        success: bool = False,
        text: Optional[str] = None,
    ) -> None:  # pragma: no cover
        ...

    @abc.abstractmethod
    async def create_comment(
        self, org: str, repo: str, pull_id: int, text: str
    ) -> str:  # pragma: no cover
        ...

    @abc.abstractmethod
    async def update_comment(
        self, org: str, repo: str, comment_id: str, text: str
    ) -> None:  # pragma: no cover
        ...

    @abc.abstractmethod
    async def download_file(
        self, org: str, repo: str, commit: str, filename: str
    ) -> AsyncIterator[bytes]:  # pragma: no cover
        yield b""

    @abc.abstractmethod
    async def file_exists(
        self, org: str, repo: str, commit: str, filename: str
    ) -> bool:  # pragma: no cover
        ...

    async def __aenter__(self):
        await self.validate()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[Exception]],
        exc_value: Optional[Exception],
        exc_traceback: Optional[traceback.StackSummary],
    ):
        await self.close()

    async def validate(self) -> None:  # pragma: no cover
        ...
