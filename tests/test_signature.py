import hmac

import pytest

from fastgithub.signature import SignatureVerificationSHA1, SignatureVerificationSHA256


@pytest.fixture
def payload() -> bytes:
    return b"foo"


@pytest.fixture
def secret() -> str:
    return "mysecret"


@pytest.fixture
def signature_sha256(payload, secret) -> str:
    digest = hmac.new(secret.encode(), payload, "sha256").hexdigest()
    return f"sha256={digest}"


def test_sha256_verification(payload: bytes, signature_sha256: str, secret: str):
    signature_checker = SignatureVerificationSHA256(secret)
    status = signature_checker._verify_signature(payload, signature_sha256)
    assert status is True


@pytest.fixture
def signature_sha1(payload, secret) -> str:
    digest = hmac.new(secret.encode(), payload, "sha1").hexdigest()
    return f"sha1={digest}"


def test_sha1_verification(payload: bytes, signature_sha1: str, secret: str):
    signature_checker = SignatureVerificationSHA1(secret)
    status = signature_checker._verify_signature(payload, signature_sha1)
    assert status is True
