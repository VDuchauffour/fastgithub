from collections.abc import Callable, Sequence
from enum import Enum

from fastapi import APIRouter

from fastgithub.handler import GithubWebhookHandler

from .helper import _inject_dependencies


def webhook_router(
    handler: GithubWebhookHandler,
    path: str = "",
    dependencies: Sequence[Callable] | None = None,
    include_in_schema: bool = True,
    tags: list[str | Enum] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
):
    router = APIRouter()
    router.add_api_route(
        path=path,
        endpoint=handler.handle,
        methods=["POST"],
        dependencies=_inject_dependencies(dependencies) or [],
        include_in_schema=include_in_schema,
        tags=tags,
        summary=summary,
        description=description,
        response_description=response_description,
    )
    return router
