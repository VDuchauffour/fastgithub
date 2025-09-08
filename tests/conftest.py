import hmac
import json

import httpx
import pytest

_BASE_URL_GITHUB_PAYLOAD = "https://raw.githubusercontent.com/octokit/webhooks/refs/heads/main/payload-examples/api.github.com/{event}/{action}.payload.json"


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


def fetch_github_payload(event: str, action: str, base_url: str = _BASE_URL_GITHUB_PAYLOAD):
    response = httpx.get(base_url.format(event=event, action=action))
    return json.loads(response.content.decode("utf8"))
