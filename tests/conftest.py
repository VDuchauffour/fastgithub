import hmac

import pytest


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


@pytest.fixture
def signature_sha1(payload, secret) -> str:
    digest = hmac.new(secret.encode(), payload, "sha1").hexdigest()
    return f"sha1={digest}"
