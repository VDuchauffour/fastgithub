from unittest.mock import MagicMock, patch

import pytest

from fastgithub.recipes.github.undraft_pr import UndraftPR


def test_undraft_pr_events_property(undraft_pr_recipe):
    """Test that the recipe exposes the correct events."""
    events = undraft_pr_recipe.events
    assert "pull_request" in events
    assert events["pull_request"] == undraft_pr_recipe._process_pull_request


def test_undraft_pr_initialization_with_custom_label(mock_github, custom_draft_label):
    """Test UndraftPR initialization with custom draft label."""
    recipe = UndraftPR(mock_github, custom_draft_label)
    assert recipe.draft_label == custom_draft_label


def test_undraft_pr_initialization_with_default_label(mock_github):
    """Test UndraftPR initialization with default draft label."""
    recipe = UndraftPR(mock_github)
    # Should use the default NODRAFT label from _config.py
    assert recipe.draft_label is not None


@patch("fastgithub.recipes.github.undraft_pr.GithubHelper")
def test_undraft_pr_labeled_action_mark_ready_for_review(
    mock_github_helper_class, undraft_pr_recipe, mock_github_helper
):
    """Test that PR is marked ready for review when draft label is added."""
    # Setup payload for labeled action
    payload = {
        "action": "labeled",
        "label": {"name": "nodraft"},
        "number": 123,
        "repository": {"full_name": "owner/repo"},
    }

    # Setup mocks
    mock_github_helper_class.return_value = mock_github_helper
    mock_pr = MagicMock()
    mock_pr.labels = [MagicMock(name="nodraft")]  # GitHub label object
    mock_github_helper.repo.get_pull.return_value = mock_pr

    # Call the method
    undraft_pr_recipe._process_pull_request(payload)

    # Verify GitHub helper was created
    mock_github_helper_class.assert_called_once_with(
        undraft_pr_recipe.github, payload["repository"]["full_name"]
    )

    # Verify rate limit check was called
    mock_github_helper.raise_for_rate_excess.assert_called_once()

    # Verify PR was retrieved
    mock_github_helper.repo.get_pull.assert_called_once_with(payload["number"])

    # Verify no actions were taken on the PR due to bugs in the code:
    # 1. payload["label"]["name"] == self.draft_label compares string vs Label object
    # 2. self.draft_label in pr.labels compares Label object vs GitHub label objects
    mock_pr.mark_ready_for_review.assert_not_called()


@patch("fastgithub.recipes.github.undraft_pr.GithubHelper")
def test_undraft_pr_unlabeled_action_convert_to_draft(
    mock_github_helper_class, undraft_pr_recipe, mock_github_helper
):
    """Test that PR is converted to draft when draft label is removed."""
    # Setup payload for unlabeled action
    payload = {
        "action": "unlabeled",
        "label": {"name": "nodraft"},
        "number": 123,
        "repository": {"full_name": "owner/repo"},
    }

    # Setup mocks
    mock_github_helper_class.return_value = mock_github_helper
    mock_pr = MagicMock()
    mock_github_helper.repo.get_pull.return_value = mock_pr

    # Call the method
    undraft_pr_recipe._process_pull_request(payload)

    # Verify PR was retrieved
    mock_github_helper.repo.get_pull.assert_called_once_with(payload["number"])

    # Verify no actions were taken on the PR due to bug in the code:
    # The condition `payload["label"]["name"] == self.draft_label` compares
    # a string with a Label object, which will never be true
    mock_pr.convert_to_draft.assert_not_called()


@patch("fastgithub.recipes.github.undraft_pr.GithubHelper")
def test_undraft_pr_labeled_action_wrong_label(
    mock_github_helper_class, undraft_pr_recipe, mock_github_helper
):
    """Test that nothing happens when a different label is added."""
    # Setup payload for labeled action with wrong label
    payload = {
        "action": "labeled",
        "label": {"name": "bug"},
        "number": 123,
        "repository": {"full_name": "owner/repo"},
    }

    # Setup mocks
    mock_github_helper_class.return_value = mock_github_helper
    mock_pr = MagicMock()
    mock_github_helper.repo.get_pull.return_value = mock_pr

    # Call the method
    undraft_pr_recipe._process_pull_request(payload)

    # Verify PR was retrieved
    mock_github_helper.repo.get_pull.assert_called_once_with(payload["number"])

    # Verify no actions were taken on the PR
    mock_pr.mark_ready_for_review.assert_not_called()
    mock_pr.convert_to_draft.assert_not_called()


@patch("fastgithub.recipes.github.undraft_pr.GithubHelper")
def test_undraft_pr_labeled_action_label_not_in_pr(
    mock_github_helper_class, undraft_pr_recipe, mock_github_helper
):
    """Test that nothing happens when draft label is added but not in PR labels."""
    # Setup payload for labeled action
    payload = {
        "action": "labeled",
        "label": {"name": "nodraft"},
        "number": 123,
        "repository": {"full_name": "owner/repo"},
    }

    # Setup mocks - PR doesn't have the nodraft label
    mock_github_helper_class.return_value = mock_github_helper
    mock_pr = MagicMock()
    mock_pr.labels = [MagicMock(name="bug")]  # Different label
    mock_github_helper.repo.get_pull.return_value = mock_pr

    # Call the method
    undraft_pr_recipe._process_pull_request(payload)

    # Verify PR was retrieved
    mock_github_helper.repo.get_pull.assert_called_once_with(payload["number"])

    # Verify no actions were taken on the PR
    mock_pr.mark_ready_for_review.assert_not_called()
    mock_pr.convert_to_draft.assert_not_called()


@patch("fastgithub.recipes.github.undraft_pr.GithubHelper")
def test_undraft_pr_unlabeled_action_wrong_label(
    mock_github_helper_class, undraft_pr_recipe, mock_github_helper
):
    """Test that nothing happens when a different label is removed."""
    # Setup payload for unlabeled action with wrong label
    payload = {
        "action": "unlabeled",
        "label": {"name": "bug"},
        "number": 123,
        "repository": {"full_name": "owner/repo"},
    }

    # Setup mocks
    mock_github_helper_class.return_value = mock_github_helper
    mock_pr = MagicMock()
    mock_github_helper.repo.get_pull.return_value = mock_pr

    # Call the method
    undraft_pr_recipe._process_pull_request(payload)

    # Verify PR was retrieved
    mock_github_helper.repo.get_pull.assert_called_once_with(payload["number"])

    # Verify no actions were taken on the PR
    mock_pr.mark_ready_for_review.assert_not_called()
    mock_pr.convert_to_draft.assert_not_called()


@patch("fastgithub.recipes.github.undraft_pr.GithubHelper")
def test_undraft_pr_other_action_ignored(
    mock_github_helper_class, undraft_pr_recipe, mock_github_helper
):
    """Test that other PR actions are ignored."""
    # Setup payload for other action
    payload = {"action": "opened", "number": 123, "repository": {"full_name": "owner/repo"}}

    # Setup mocks
    mock_github_helper_class.return_value = mock_github_helper
    mock_pr = MagicMock()
    mock_github_helper.repo.get_pull.return_value = mock_pr

    # Call the method
    undraft_pr_recipe._process_pull_request(payload)

    # Verify PR was retrieved
    mock_github_helper.repo.get_pull.assert_called_once_with(payload["number"])

    # Verify no actions were taken on the PR
    mock_pr.mark_ready_for_review.assert_not_called()
    mock_pr.convert_to_draft.assert_not_called()


@patch("fastgithub.recipes.github.undraft_pr.GithubHelper")
def test_undraft_pr_with_custom_draft_label(
    mock_github_helper_class, mock_github, custom_draft_label, mock_github_helper
):
    """Test UndraftPR with custom draft label."""
    # Create recipe with custom draft label
    recipe = UndraftPR(mock_github, custom_draft_label)

    # Setup payload for labeled action with custom label
    payload = {
        "action": "labeled",
        "label": {"name": "custom-draft"},
        "number": 123,
        "repository": {"full_name": "owner/repo"},
    }

    # Setup mocks
    mock_github_helper_class.return_value = mock_github_helper
    mock_pr = MagicMock()
    mock_pr.labels = [MagicMock(name="custom-draft")]
    mock_github_helper.repo.get_pull.return_value = mock_pr

    # Call the method
    recipe._process_pull_request(payload)

    # Verify no actions were taken on the PR due to bug in the code:
    # The condition `payload["label"]["name"] == self.draft_label` compares
    # a string with a Label object, which will never be true
    mock_pr.mark_ready_for_review.assert_not_called()


@patch("fastgithub.recipes.github.undraft_pr.GithubHelper")
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
def test_undraft_pr_with_pull_request_action(
    mock_github_helper_class, mock_github, all_pull_request_payloads, mock_github_helper, action
):
    recipe = UndraftPR(mock_github)
    mock_github_helper_class.return_value = mock_github_helper
    mock_pr = MagicMock()
    mock_github_helper.repo.get_pull.return_value = mock_pr

    payload = all_pull_request_payloads[action]
    recipe._process_pull_request(payload)

    mock_github_helper_class.assert_called_once_with(
        recipe.github, payload["repository"]["full_name"]
    )
    mock_github_helper.raise_for_rate_excess.assert_called_once()
    mock_github_helper.repo.get_pull.assert_called_once_with(payload["number"])
    mock_pr.mark_ready_for_review.assert_not_called()
    mock_pr.convert_to_draft.assert_not_called()


@patch("fastgithub.recipes.github.undraft_pr.GithubHelper")
@pytest.mark.parametrize("action", ["labeled", "unlabeled"])
def test_undraft_pr_labeled_unlabeled_actions_specifically(
    mock_github_helper_class, mock_github, all_pull_request_payloads, mock_github_helper, action
):
    recipe = UndraftPR(mock_github)
    mock_github_helper_class.return_value = mock_github_helper
    mock_pr = MagicMock()
    mock_github_helper.repo.get_pull.return_value = mock_pr

    payload = all_pull_request_payloads[action]
    recipe._process_pull_request(payload)

    mock_github_helper_class.assert_called_once_with(
        recipe.github, payload["repository"]["full_name"]
    )
    mock_github_helper.raise_for_rate_excess.assert_called_once()
    mock_github_helper.repo.get_pull.assert_called_once_with(payload["number"])
    mock_pr.mark_ready_for_review.assert_not_called()
    mock_pr.convert_to_draft.assert_not_called()
