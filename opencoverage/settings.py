from typing import List, Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    timeout_keep_alive: int = 10
    proxy_headers: bool = True

    public_url: Optional[str] = None

    dsn: str

    cors: List[str] = []

    scm: str
    github_app_id: Optional[str]
    github_app_pem_file: Optional[str]
    github_installation_id: Optional[str]
