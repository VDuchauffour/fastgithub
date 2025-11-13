from unittest.mock import MagicMock, patch

import pytest

from fastgithub.recipes.github.labels_from_commits import LabelsFromCommits


@pytest.fixture
def labels_from_commits_recipe(mock_github, custom_labels_config):
    """Create LabelsFromCommits instance with mocked GitHub."""
    return LabelsFromCommits(mock_github, custom_labels_config)


def test_labels_from_commits_events_property(labels_from_commits_recipe):
    """Test that the recipe exposes the correct events."""
    events = labels_from_commits_recipe.events
    assert "pull_request" in events
    assert events["pull_request"] == labels_from_commits_recipe._process_push


def test_labels_from_commits_initialization_with_custom_config(mock_github, custom_labels_config):
    """Test LabelsFromCommits initialization with custom labels config."""
    recipe = LabelsFromCommits(mock_github, custom_labels_config)
    assert recipe.labels_config == custom_labels_config


def test_labels_from_commits_initialization_with_default_config(mock_github):
    """Test LabelsFromCommits initialization with default labels config."""
    recipe = LabelsFromCommits(mock_github)
    # Should use the default LABEL_CONFIG from _config.py
    assert recipe.labels_config is not None


@patch("fastgithub.recipes.github.labels_from_commits.GithubHelper")
def test_labels_from_commits_successful_label_extraction(
    mock_github_helper_class,
    labels_from_commits_recipe,
    sample_pull_request_payload,
    mock_github_helper,
):
    mock_github_helper_class.return_value = mock_github_helper
    mock_pr = MagicMock()
    mock_github_helper.repo.get_pull.return_value = mock_pr
    mock_github_helper.extract_labels_from_pr.return_value = {"bug", "feature"}
    mock_github_helper.add_labels_to_pr = MagicMock()

    labels_from_commits_recipe._process_push(sample_pull_request_payload)

    mock_github_helper_class.assert_called_once_with(
        labels_from_commits_recipe.github, sample_pull_request_payload["repository"]["full_name"]
    )
    mock_github_helper.raise_for_rate_excess.assert_called_once()
    mock_github_helper.repo.get_pull.assert_called_once_with(sample_pull_request_payload["number"])
    mock_github_helper.extract_labels_from_pr.assert_called_once_with(
        mock_pr, labels_from_commits_recipe.labels_config
    )
    mock_github_helper.add_labels_to_pr.assert_called_once_with(mock_pr, {"bug", "feature"})


@patch("fastgithub.recipes.github.labels_from_commits.GithubHelper")
def test_labels_from_commits_no_labels_extracted(
    mock_github_helper_class,
    labels_from_commits_recipe,
    sample_pull_request_payload,
    mock_github_helper,
):
    mock_github_helper_class.return_value = mock_github_helper
    mock_pr = MagicMock()
    mock_github_helper.repo.get_pull.return_value = mock_pr
    mock_github_helper.extract_labels_from_pr.return_value = set()
    mock_github_helper.add_labels_to_pr = MagicMock()

    labels_from_commits_recipe._process_push(sample_pull_request_payload)

    mock_github_helper.extract_labels_from_pr.assert_called_once()
    mock_github_helper.add_labels_to_pr.assert_not_called()


@patch("fastgithub.recipes.github.labels_from_commits.GithubHelper")
def test_labels_from_commits_with_default_config(
    mock_github_helper_class, mock_github, sample_pull_request_payload, mock_github_helper
):
    recipe = LabelsFromCommits(mock_github)
    mock_github_helper_class.return_value = mock_github_helper
    mock_pr = MagicMock()
    mock_github_helper.repo.get_pull.return_value = mock_pr
    mock_github_helper.extract_labels_from_pr.return_value = {"nodraft"}
    mock_github_helper.add_labels_to_pr = MagicMock()

    recipe._process_push(sample_pull_request_payload)

    mock_github_helper.extract_labels_from_pr.assert_called_once_with(
        mock_pr, recipe.labels_config
    )


@patch("fastgithub.recipes.github.labels_from_commits.GithubHelper")
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
def test_labels_from_commits_with_pull_request_action(
    mock_github_helper_class, mock_github, all_pull_request_payloads, mock_github_helper, action
):
    recipe = LabelsFromCommits(mock_github)
    mock_github_helper_class.return_value = mock_github_helper
    mock_pr = MagicMock()
    mock_github_helper.repo.get_pull.return_value = mock_pr
    mock_github_helper.extract_labels_from_pr.return_value = {"bug"}
    mock_github_helper.add_labels_to_pr = MagicMock()

    payload = all_pull_request_payloads[action]
    recipe._process_push(payload)

    mock_github_helper_class.assert_called_once_with(
        recipe.github, payload["repository"]["full_name"]
    )
    mock_github_helper.raise_for_rate_excess.assert_called_once()
    mock_github_helper.repo.get_pull.assert_called_once_with(payload["number"])
    mock_github_helper.extract_labels_from_pr.assert_called_once_with(
        mock_pr, recipe.labels_config
    )
    mock_github_helper.add_labels_to_pr.assert_called_once_with(mock_pr, {"bug"})
