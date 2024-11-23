import pytest

from fastgithub.handler import GithubWebhookHandler
from fastgithub.signature import SignatureVerificationSHA256


def test_safe_mode_if_signature_verification_is_provided(secret):
    signature_verification = SignatureVerificationSHA256(secret)
    webhook_handler = GithubWebhookHandler(signature_verification)
    assert webhook_handler.safe_mode is True


def test_safe_mode_if_signature_verification_is_not_provided(secret):
    webhook_handler = GithubWebhookHandler(signature_verification=None)
    assert webhook_handler.safe_mode is False


def test_function_is_append_using_decorator():
    webhook_handler = GithubWebhookHandler(signature_verification=None)

    @webhook_handler.listen("push")
    def foo():
        pass

    assert webhook_handler.webhooks["push"] == [foo]
    assert webhook_handler.webhooks == webhook_handler._webhooks


def test_function_is_append_using_list():
    webhook_handler = GithubWebhookHandler(signature_verification=None)

    def foo():
        pass

    def bar():
        pass

    webhook_handler.listen("push", [foo, bar])

    assert webhook_handler.webhooks["push"] == [foo, bar]
    assert webhook_handler.webhooks == webhook_handler._webhooks


@pytest.mark.asyncio
async def test_process_event():
    webhook_handler = GithubWebhookHandler(signature_verification=None)

    def foo(*args, **kwargs):
        pass

    def bar(*args, **kwargs):
        raise

    webhook_handler.listen("push", [foo])
    assert await webhook_handler.process_event("push", {}) is True
    webhook_handler.listen("pull_request", [bar])
    assert await webhook_handler.process_event("pull_request", {}) is False
