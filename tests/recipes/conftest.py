import json
from unittest.mock import MagicMock

import httpx
import pytest

from fastgithub.helpers.github import Label
from fastgithub.recipes.github.autocreate_pr import AutoCreatePullRequest
from fastgithub.recipes.github.undraft_pr import UndraftPR

# see https://github.com/octokit/webhooks/tree/main/payload-examples/api.github.com
_BASE_URL_GITHUB_PAYLOAD = "https://raw.githubusercontent.com/octokit/webhooks/refs/heads/main/payload-examples/api.github.com/{event}/{action}"


@pytest.fixture
def mock_github():
    """Mock GitHub instance."""
    return MagicMock()


@pytest.fixture
def mock_github_helper():
    """Mock GithubHelper instance."""
    helper = MagicMock()
    helper.repo = MagicMock()
    helper.raise_for_rate_excess = MagicMock()
    return helper


def fetch_github_payload(event: str, action: str, base_url: str = _BASE_URL_GITHUB_PAYLOAD):
    response = httpx.get(base_url.format(event=event, action=action))
    return json.loads(response.content.decode("utf8"))


def fetch_all_pull_request_payloads():
    """
    Fetch all available pull_request event payloads from GitHub webhooks repository.

    Returns:
        dict: Dictionary mapping action names to their corresponding payloads
    """

    # All available pull_request actions from the GitHub webhooks repository
    # Based on actual files available at: https://github.com/octokit/webhooks/tree/main/payload-examples/api.github.com/pull_request
    actions = [
        "assigned",
        "closed",
        "converted_to_draft",
        "labeled",
        "locked",
        "opened",
        "ready_for_review",
        "reopened",
        "review_request_removed",
        "review_requested",
        "synchronize",
        "unassigned",
        "unlabeled",
        "unlocked",
    ]

    return {
        action: fetch_github_payload("pull_request", action + ".payload.json")
        for action in actions
    }


@pytest.fixture
def all_pull_request_payloads():
    """Fixture that provides all available pull_request payloads."""
    return fetch_all_pull_request_payloads()


@pytest.fixture
def push_payload():
    """Get a valid GitHub push payload."""
    return fetch_github_payload("push", "payload.json")


@pytest.fixture
def sample_pull_request_payload():
    return {
        "action": "opened",
        "number": 123,
        "pull_request": {
            "number": 123,
            "title": "Test PR",
            "body": "Test PR body",
            "head": {"ref": "feature-branch"},
            "base": {"ref": "main"},
        },
        "repository": {"full_name": "owner/repo", "name": "repo", "owner": {"login": "owner"}},
    }


@pytest.fixture
def custom_labels_config():
    return {
        "#bug": [Label(name="bug", color="d73a4a", description="Something isn't working")],
        "#feature": [Label(name="feature", color="a2eeef", description="New feature")],
    }


@pytest.fixture
def autocreate_pr_recipe(mock_github):
    return AutoCreatePullRequest(mock_github)


@pytest.fixture
def undraft_pr_recipe(mock_github):
    """Create UndraftPR instance with mocked GitHub."""
    return UndraftPR(mock_github)


@pytest.fixture
def custom_draft_label():
    """Custom draft label for testing."""
    return Label(name="custom-draft", color="cccccc", description="Custom draft label")
