import collections
import fnmatch
from collections.abc import Sequence

from fastapi import HTTPException, Request

from fastgithub.recipes import Recipe
from fastgithub.types import Payload

from .signature import SignatureVerification


class GithubWebhookHandler:
    def __init__(self, signature_verification: SignatureVerification | None) -> None:
        self._webhooks = collections.defaultdict(list)
        self._signature_verification = signature_verification

    @property
    def webhooks(self) -> dict[str, list[Recipe]]:
        return self._webhooks

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

    @staticmethod
    def _check_recipe_event_processing(recipe: Recipe, event: str):
        return any(fnmatch.fnmatch(recipe_event, event) for recipe_event in recipe.events)

    async def process_event(self, event: str, payload: Payload) -> bool:
        """Process the GitHub event. Override this method to handle specific events.

        Args:
            event (str): The type of GitHub event (e.g., 'push', 'pull_request').
            data (Payload): The payload of the event.

        Returns:
            bool: True if the process handle well, otherwise False.
        """
        try:
            for recipe in self.webhooks[event]:
                if self._check_recipe_event_processing(recipe, event):
                    recipe(payload)
        except:  # noqa: E722
            return False
        else:
            return True

    def listen(self, event: str, recipes: Sequence[Recipe]) -> None:
        self._webhooks[event].extend(recipes)
