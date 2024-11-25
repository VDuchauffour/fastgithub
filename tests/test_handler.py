import pytest

from fastgithub import GithubWebhookHandler, Recipe, SignatureVerificationSHA256
from fastgithub.types import Payload


def test_safe_mode_if_signature_verification_is_provided(secret):
    signature_verification = SignatureVerificationSHA256(secret)
    webhook_handler = GithubWebhookHandler(signature_verification)
    assert webhook_handler.safe_mode is True


def test_safe_mode_if_signature_verification_is_not_provided(secret):
    webhook_handler = GithubWebhookHandler(signature_verification=None)
    assert webhook_handler.safe_mode is False


def test_recipes_is_append():
    webhook_handler = GithubWebhookHandler(signature_verification=None)

    class Foo(Recipe):
        def execute(self, payload: Payload) -> None:
            pass

    class Bar(Recipe):
        def execute(self, payload: Payload) -> None:
            pass

    recipes = [Foo(), Bar()]
    webhook_handler.listen("push", recipes)

    for recipe, recipe_type in zip(webhook_handler.webhooks["push"], recipes):
        assert isinstance(recipe, type(recipe_type))
    assert len(webhook_handler.webhooks["push"]) == 2
    assert webhook_handler.webhooks == webhook_handler._webhooks


def test_triggered_event_match_recipe_event_definitions():
    webhook_handler = GithubWebhookHandler(signature_verification=None)

    class Foo(Recipe):
        events = ["push"]

        def __call__(self, payload: Payload) -> None:
            pass

    event = "push"
    webhook_handler.listen(event, [Foo()])
    recipe = webhook_handler.webhooks[event][0]
    assert webhook_handler._check_recipe_event_processing(recipe, event) is True

    event = "pull_request"
    assert webhook_handler._check_recipe_event_processing(recipe, event) is False

    assert webhook_handler._check_recipe_event_processing(recipe, "*") is True


@pytest.mark.asyncio
async def test_process_event():
    webhook_handler = GithubWebhookHandler(signature_verification=None)

    class Foo(Recipe):
        def __call__(self, payload: Payload) -> None:
            pass

    class Bar(Recipe):
        def __call__(self, payload: Payload) -> None:
            raise

    webhook_handler.listen("push", [Foo()])
    assert await webhook_handler.process_event("push", {}) is True
    webhook_handler.listen("pull_request", [Bar()])
    assert await webhook_handler.process_event("pull_request", {}) is False
