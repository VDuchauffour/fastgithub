from fastgithub.handler import GithubWebhookHandler
from fastgithub.signature import SignatureVerificationSHA256


def test_safe_mode_if_signature_verification_is_provided(secret):
    signature_verification = SignatureVerificationSHA256(secret)
    webhook_handler = GithubWebhookHandler(signature_verification)
    assert webhook_handler.safe_mode is True


def test_safe_mode_if_signature_verification_is_not_provided(secret):
    webhook_handler = GithubWebhookHandler(signature_verification=None)
    assert webhook_handler.safe_mode is False
