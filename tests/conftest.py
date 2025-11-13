import hmac

import pytest


@pytest.fixture
def signature_payload() -> bytes:
    return b"foo"


@pytest.fixture
def signature_secret() -> str:
    return "mysecret"


@pytest.fixture
def signature_sha256(signature_payload: bytes, signature_secret: str) -> str:
    digest = hmac.new(signature_secret.encode(), signature_payload, "sha256").hexdigest()
    return f"sha256={digest}"


@pytest.fixture
def signature_sha1(signature_payload: bytes, signature_secret: str) -> str:
    digest = hmac.new(signature_secret.encode(), signature_payload, "sha1").hexdigest()
    return f"sha1={digest}"
