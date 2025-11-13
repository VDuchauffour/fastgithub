import pytest


@pytest.mark.parametrize(
    "action",
    [
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
    ],
)
def test_pull_request_payload_structure(all_pull_request_payloads, action):
    required_fields = ["action", "number", "repository"]
    payload = all_pull_request_payloads[action]

    for field in required_fields:
        assert field in payload, f"Payload for action '{action}' missing required field '{field}'"
    assert "full_name" in payload["repository"], (
        f"Repository missing 'full_name' in action '{action}'"
    )
    assert payload["action"] == action, (
        f"Payload action '{payload['action']}' doesn't match key '{action}'"
    )
    assert isinstance(payload["number"], int), f"PR number should be integer in action '{action}'"


def test_all_pull_request_payloads_actions_coverage(all_pull_request_payloads):
    expected_actions = [
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

    found_actions = set(all_pull_request_payloads.keys())
    common_actions = {"opened", "closed", "labeled", "unlabeled"}
    assert common_actions.issubset(found_actions), (
        f"Missing common actions. Found: {found_actions}"
    )

    print(f"Successfully fetched payloads for actions: {sorted(found_actions)}")
    missing_actions = set(expected_actions) - found_actions
    if missing_actions:
        print(f"Missing payloads for actions: {sorted(missing_actions)}")
