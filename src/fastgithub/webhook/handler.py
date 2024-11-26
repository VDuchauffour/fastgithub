import collections
import fnmatch
import itertools
from collections.abc import Callable, Sequence
from typing import overload

from fastapi import HTTPException, Request

from fastgithub.recipes import Recipe
from fastgithub.types import Payload

from .signature import SignatureVerification


class GithubWebhookHandler:
    def __init__(self, signature_verification: SignatureVerification | None) -> None:
        self._signature_verification = signature_verification
        self._webhooks = collections.defaultdict(list)
        self._recipes = []

    @property
    def webhooks(self) -> dict[str, list[Callable]]:
        return self._webhooks

    @property
    def recipes(self) -> list[Callable]:
        return self._recipes

    @property
    def signature_verification(self) -> SignatureVerification | None:
        return self._signature_verification

    @property
    def safe_mode(self) -> bool:
        return bool(self.signature_verification)

    async def handle(self, request: Request):
        """Handle incoming webhook events from GitHub."""
        if self.safe_mode:
            await self.signature_verification.verify(request)  # type: ignore

        event = request.headers.get("X-GitHub-Event")
        data = await request.json()

        if event is not None:
            status = await self.process_event(event, data)
            if status:
                return {"status": "success"}
            else:
                raise HTTPException(status_code=400, detail="Error during {event} event!")
        raise HTTPException(status_code=422, detail="No event provided!")

    def _infer_event_recipes(self, event: str) -> list[Callable]:
        webhook_recipes = [
            webhook_recipes
            for webhook_event, webhook_recipes in self.webhooks.items()
            if fnmatch.fnmatch(event, webhook_event)
        ]
        return list(itertools.chain.from_iterable(webhook_recipes))

    async def process_event(self, event: str, payload: Payload) -> bool:
        """Process the GitHub event. Override this method to handle specific events.

        Args:
            event (str): The type of GitHub event (e.g., 'push', 'pull_request').
            data (Payload): The payload of the event.

        Returns:
            bool: True if the process handle well, otherwise False.
        """
        try:
            webhook_recipes = self._infer_event_recipes(event)
            for recipe in webhook_recipes:
                recipe(payload)
        except:  # noqa: E722
            return False
        else:
            return True

    @overload
    def listen(self, event: str) -> Callable: ...

    @overload
    def listen(self, event: str, recipes: list[Callable]) -> Callable: ...

    def listen(self, event: str, recipes: Sequence[Callable] | None = None) -> Callable | None:
        if recipes is None:

            def decorator(func):
                self.listen(event, [func])
                return func

            return decorator
        else:
            if any(not isinstance(recipe, Callable) for recipe in recipes):
                raise ValueError(
                    f"{self.listen.__name__} works only with functions, use {self.plan.__name__} with {Recipe.__name__}!"  # noqa: E501
                )
            self.webhooks[event].extend(recipes)
            self.recipes.extend(recipes)

    def plan(self, recipes: Sequence[Recipe]) -> None:
        for recipe in recipes:
            for event, func in recipe.events.items():
                self.listen(event, [func])
