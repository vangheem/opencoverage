from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from opencoverage.database import Database
from opencoverage.settings import Settings

router = APIRouter()


class HTTPApplication(FastAPI):
    def __init__(self, settings: Settings):
        super().__init__(title="API")
        self.include_router(router)

        self.db = Database(settings)

        self.settings = settings

        self.add_event_handler("startup", self.initialize)
        self.add_event_handler("shutdown", self.finalize)

    async def initialize(self) -> None:
        self.add_middleware(
            CORSMiddleware,
            allow_origins=self.settings.cors,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        await self.db.initialize()

    async def finalize(self) -> None:
        await self.db.finalize()
