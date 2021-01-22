import argparse
import dotenv
import asyncio

import uvicorn

from opencoverage.api.app import HTTPApplication

from .settings import Settings

parser = argparse.ArgumentParser(description="command runner", add_help=False)
parser.add_argument(
    "-e",
    "--env-file",
    help="Env file",
)


def run_command():
    asyncio.run(_run())


async def _run():
    arguments, _ = parser.parse_known_args()
    if arguments.env_file:
        dotenv.load_dotenv(arguments.env_file)

    settings = Settings()
    app = HTTPApplication(settings)
    configuration = uvicorn.Config(
        app,
        port=settings.port,
        host=settings.host,
        timeout_keep_alive=settings.timeout_keep_alive,
        proxy_headers=settings.proxy_headers,
        log_config=None,
    )
    server = uvicorn.Server(config=configuration)
    print(f"Running server: {settings}")
    await server.serve()
