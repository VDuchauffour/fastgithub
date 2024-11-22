import collections
import hashlib
import hmac
import os
from collections.abc import Callable
from typing import overload

from fastapi import HTTPException, Request

# TODO handle ratelimit github api (as middleware?)
# TODO fix safe mode
# TODO recipe helpers + faire class pour recipes  + listen raw function et recipe
# TODO try except


class GithubWebhookHandler:
    def __init__(self, token: str | None = None, unsafe_mode: bool = False) -> None:
        self._token = token or os.environ["GITHUB_TOKEN"]
        self._webhooks = collections.defaultdict(list)
        self._unsafe_mode = unsafe_mode

    @property
    def token(self) -> str:
        return self._token

    @property
    def webhooks(self) -> dict[str, list[Callable]]:
        return self._webhooks

    async def _verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify the GitHub webhook signature.

        Args:
            payload (bytes): The raw request payload.
            signature (str): The signature provided by GitHub in the header.

        Returns:
            bool: True if the signature is valid, otherwise False.
        """
        if not signature:
            return False

        hash_alg, provided_signature = signature.split("=")
        computed_signature = hmac.new(
            self.token.encode(),
            payload,
            hashlib.new(hash_alg).name,
        ).hexdigest()

        return hmac.compare_digest(provided_signature, computed_signature)

    async def _safety_checks(self, request: Request):
        signature = request.headers.get("X-Hub-Signature-256")
        if not signature:
            raise HTTPException(status_code=400, detail="Signature is missing")

        payload = await request.body()

        if not await self._verify_signature(payload, signature):
            raise HTTPException(status_code=403, detail="Invalid signature")

    async def handle(self, request: Request):
        """Handle incoming webhook events from GitHub."""
        if not self._unsafe_mode:
            await self._safety_checks(request)

        event = request.headers.get("X-GitHub-Event")
        data = await request.json()

        if event is not None:
            status = await self.process_event(event, data)
            if status:
                return {"status": "success"}
            else:
                raise HTTPException(status_code=400, detail="Error during {event} event!")
        raise HTTPException(status_code=422, detail="No event provided!")

    async def process_event(self, event: str, data: dict) -> bool:
        """Process the GitHub event. Override this method to handle specific events.

        Args:
            event (str): The type of GitHub event (e.g., 'push', 'pull_request').
            data (dict): The payload of the event.

        Returns:
            bool: True if the process handle well, otherwise False.
        """
        try:
            for hook in self.webhooks[event]:
                hook(data)
        except:  # noqa: E722
            return False
        else:
            return True

    @overload
    def listen(self, event: str) -> Callable:
        pass

    @overload
    def listen(self, event: str, functions: list[Callable]) -> Callable:
        pass

    def listen(self, event: str, functions: list[Callable] | None = None) -> Callable | None:
        if functions is None:

            def decorator(func: Callable):
                assert func is not None  # noqa: S101
                self._webhooks[event].append(func)
                return func

            return decorator
        else:
            for func in functions:
                self._webhooks[event].append(func)
