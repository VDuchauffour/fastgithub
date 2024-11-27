from collections.abc import Callable

import pytest

from fastgithub import GithubWebhookHandler, Recipe, SignatureVerificationSHA256
from fastgithub.types import Payload


@pytest.fixture
def webhook_handler() -> GithubWebhookHandler:
    return GithubWebhookHandler(signature_verification=None)


def test_safe_mode_if_signature_verification_is_provided(secret):
    signature_verification = SignatureVerificationSHA256(secret)
    webhook_handler = GithubWebhookHandler(signature_verification)
    assert webhook_handler.safe_mode is True


def test_safe_mode_if_signature_verification_is_not_provided(webhook_handler):
    assert webhook_handler.safe_mode is False


def test_recipes_is_append_with_listen_method(webhook_handler):
    def foo(payload: Payload) -> None:
        pass

    recipes = [foo]
    webhook_handler.listen("push", recipes)

    assert len(webhook_handler.webhooks["push"]) == 1


def test_recipes_is_append_with_listen_method_as_decorator(webhook_handler):
    @webhook_handler.listen("push")
    def foo(payload: Payload) -> None:
        pass

    assert len(webhook_handler.webhooks["push"]) == 1
    assert len(webhook_handler.recipes) == 1


def test_recipes_is_append_with_plan_method(webhook_handler):
    class Foo(Recipe):
        @property
        def events(self) -> dict[str, Callable]:
            return {"push": self.__call__}

        def __call__(self, payload: Payload) -> None:
            pass

    class Bar(Recipe):
        @property
        def events(self) -> dict[str, Callable]:
            return {"push": self.__call__}

        def __call__(self, payload: Payload) -> None:
            pass

    recipes = [Foo(), Bar()]
    webhook_handler.plan(recipes)

    assert len(webhook_handler.webhooks["push"]) == 2
    assert len(webhook_handler.recipes) == 2


def test_triggered_event_match_recipe_event_definitions(webhook_handler):
    class Foo(Recipe):
        @property
        def events(self) -> dict[str, Callable]:
            return {"push": self.__call__}

        def __call__(self, payload: Payload) -> None:
            pass

    event = "push"
    webhook_handler.plan([Foo()])

    assert len(webhook_handler.recipes) == 1

    assert len(webhook_handler.webhooks[event]) == 1

    event = "pull_request"
    assert len(webhook_handler.webhooks[event]) == 0


@pytest.mark.asyncio
async def test_process_event_return_right_value(webhook_handler):
    class Foo(Recipe):
        @property
        def events(self) -> dict[str, Callable]:
            return {"push": self.__call__}

        def __call__(self, payload: Payload) -> None:
            pass

    class Bar(Recipe):
        @property
        def events(self) -> dict[str, Callable]:
            return {"pull_request": self.__call__}

        def __call__(self, payload: Payload) -> None:
            raise

    webhook_handler.listen("push", [Foo()])
    assert await webhook_handler.process_event("push", {}) is True
    webhook_handler.listen("pull_request", [Bar()])
    assert await webhook_handler.process_event("pull_request", {}) is False


@pytest.mark.asyncio
async def test_process_event_filtering_match_correct_events_with_listen_method(webhook_handler):
    def foo(payload: Payload):
        pass

    def bar(payload: Payload):
        pass

    def baz(payload: Payload):
        pass

    webhook_handler.listen("push", [foo])
    webhook_handler.listen("pull_request", [bar])
    webhook_handler.listen("*", [baz])

    push_recipes = webhook_handler._infer_event_recipes("push")
    assert len(push_recipes) == 2
    assert push_recipes[0] == foo
    assert push_recipes[1] == baz

    pr_recipes = webhook_handler._infer_event_recipes("pull_request")
    assert len(pr_recipes) == 2
    assert pr_recipes[0] == bar
    assert pr_recipes[1] == baz

    all_recipes = webhook_handler._infer_event_recipes("*")
    assert len(all_recipes) == 1
    assert all_recipes[0] == baz


@pytest.mark.asyncio
async def test_process_event_filtering_match_correct_events_with_plan_method(webhook_handler):
    class Foo(Recipe):
        @property
        def events(self) -> dict[str, Callable]:
            return {"push": self.__call__}

        def __call__(self, payload: Payload) -> None:
            pass

    class Bar(Recipe):
        @property
        def events(self) -> dict[str, Callable]:
            return {"pull_request": self.__call__}

        def __call__(self, payload: Payload) -> None:
            pass

    class Baz(Recipe):
        @property
        def events(self) -> dict[str, Callable]:
            return {"*": self.__call__}

        def __call__(self, payload: Payload) -> None:
            pass

    webhook_handler.plan([Foo(), Bar(), Baz()])

    push_recipes = webhook_handler._infer_event_recipes("push")
    assert len(push_recipes) == 2
    assert push_recipes[0].__name__ == Foo.__call__.__name__
    assert isinstance(push_recipes[0].__self__, Foo)
    assert push_recipes[1].__name__ == Baz.__call__.__name__
    assert isinstance(push_recipes[1].__self__, Baz)

    pr_recipes = webhook_handler._infer_event_recipes("pull_request")
    assert len(pr_recipes) == 2
    assert pr_recipes[0].__name__ == Bar.__call__.__name__
    assert isinstance(pr_recipes[0].__self__, Bar)
    assert pr_recipes[1].__name__ == Baz.__call__.__name__
    assert isinstance(pr_recipes[1].__self__, Baz)

    all_recipes = webhook_handler._infer_event_recipes("*")
    assert len(all_recipes) == 1
    assert all_recipes[0].__name__ == Baz.__call__.__name__
    assert isinstance(all_recipes[0].__self__, Baz)
