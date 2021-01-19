from opencoverage.settings import Settings

from .base import SCMClient
from .github import Github


def get_client(settings: Settings) -> SCMClient:
    if settings.scm == "github":
        return Github(settings)
    else:
        raise TypeError(
            f"Must provide valid SCM value, allowed: [github], provided: {settings.scm}"
        )
