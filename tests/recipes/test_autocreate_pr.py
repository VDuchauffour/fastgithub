from unittest.mock import MagicMock, patch

import pytest
from github.GithubException import GithubException


def test_autocreate_pr_events_property(autocreate_pr_recipe):
    events = autocreate_pr_recipe.events
    assert "push" in events
    assert events["push"] == autocreate_pr_recipe._process_push


@patch("fastgithub.recipes.github.autocreate_pr.GithubHelper")
def test_autocreate_pr_successful_creation(
    mock_github_helper_class, autocreate_pr_recipe, push_payload, mock_github_helper
):
    mock_github_helper_class.return_value = mock_github_helper
    mock_github_helper.repo.default_branch = "main"
    mock_github_helper.repo.get_commits.return_value = [
        MagicMock(commit=MagicMock(message="Test commit"))
    ]
    mock_github_helper.repo.create_pull.return_value = MagicMock()

    autocreate_pr_recipe._process_push(push_payload)

    mock_github_helper_class.assert_called_once_with(
        autocreate_pr_recipe.github, repo_fullname=push_payload["repository"]["full_name"]
    )
    mock_github_helper.raise_for_rate_excess.assert_called_once()
    mock_github_helper.repo.create_pull.assert_called_once_with(
        base="main",
        head=push_payload["ref"],
        title="Test commit",
        body="Created by FastGitHub",
        draft=True,
    )


@patch("fastgithub.recipes.github.autocreate_pr.GithubHelper")
def test_autocreate_pr_with_custom_parameters(
    mock_github_helper_class, autocreate_pr_recipe, push_payload, mock_github_helper
):
    """Test PR creation with custom parameters."""
    # Setup mocks
    mock_github_helper_class.return_value = mock_github_helper
    mock_github_helper.repo.create_pull.return_value = MagicMock()

    # Call with custom parameters
    autocreate_pr_recipe._process_push(
        push_payload,
        base_branch="develop",
        title="Custom Title",
        body="Custom body",
        as_draft=False,
    )

    # Verify PR creation with custom parameters
    mock_github_helper.repo.create_pull.assert_called_once_with(
        base="develop",
        head=push_payload["ref"],
        title="Custom Title",
        body="Custom body",
        draft=False,
    )


@patch("fastgithub.recipes.github.autocreate_pr.GithubHelper")
def test_autocreate_pr_github_exception_422_ignored(
    mock_github_helper_class, autocreate_pr_recipe, push_payload, mock_github_helper
):
    """Test that GithubException with status 422 is ignored (PR already exists)."""
    # Setup mocks
    mock_github_helper_class.return_value = mock_github_helper
    mock_github_helper.repo.default_branch = "main"
    mock_github_helper.repo.get_commits.return_value = [
        MagicMock(commit=MagicMock(message="Test commit"))
    ]

    # Mock GithubException with status 422
    mock_github_helper.repo.create_pull.side_effect = GithubException(422, {}, {})

    # Should not raise an exception
    autocreate_pr_recipe._process_push(push_payload)

    # Verify create_pull was called
    mock_github_helper.repo.create_pull.assert_called_once()


@patch("fastgithub.recipes.github.autocreate_pr.GithubHelper")
def test_autocreate_pr_github_exception_other_status_raised(
    mock_github_helper_class, autocreate_pr_recipe, push_payload, mock_github_helper
):
    """Test that GithubException with status other than 422 is raised."""
    # Setup mocks
    mock_github_helper_class.return_value = mock_github_helper
    mock_github_helper.repo.default_branch = "main"
    mock_github_helper.repo.get_commits.return_value = [
        MagicMock(commit=MagicMock(message="Test commit"))
    ]

    # Mock GithubException with status 500
    mock_github_helper.repo.create_pull.side_effect = GithubException(500, {}, {})

    # Should raise the exception
    with pytest.raises(GithubException) as exc_info:
        autocreate_pr_recipe._process_push(push_payload)

    assert exc_info.value.status == 500


@patch("fastgithub.recipes.github.autocreate_pr.GithubHelper")
def test_autocreate_pr_uses_commit_message_as_title_when_no_title_provided(
    mock_github_helper_class, autocreate_pr_recipe, push_payload, mock_github_helper
):
    """Test that commit message is used as title when no title is provided."""
    # Setup mocks
    mock_github_helper_class.return_value = mock_github_helper
    mock_github_helper.repo.default_branch = "main"
    mock_commit = MagicMock(commit=MagicMock(message="Amazing feature commit"))
    mock_github_helper.repo.get_commits.return_value = [mock_commit]
    mock_github_helper.repo.create_pull.return_value = MagicMock()

    # Call without title parameter
    autocreate_pr_recipe._process_push(push_payload)

    # Verify get_commits was called to get the commit message
    mock_github_helper.repo.get_commits.assert_called_once_with(sha=push_payload["ref"])

    # Verify PR creation uses commit message as title
    mock_github_helper.repo.create_pull.assert_called_once_with(
        base="main",
        head=push_payload["ref"],
        title="Amazing feature commit",
        body="Created by FastGitHub",
        draft=True,
    )


@patch("fastgithub.recipes.github.autocreate_pr.GithubHelper")
def test_autocreate_pr_uses_custom_base_branch(
    mock_github_helper_class, autocreate_pr_recipe, push_payload, mock_github_helper
):
    """Test that custom base_branch is used instead of default branch."""
    # Setup mocks
    mock_github_helper_class.return_value = mock_github_helper
    mock_github_helper.repo.default_branch = "main"
    mock_github_helper.repo.get_commits.return_value = [
        MagicMock(commit=MagicMock(message="Test commit"))
    ]
    mock_github_helper.repo.create_pull.return_value = MagicMock()

    # Call with custom base_branch
    autocreate_pr_recipe._process_push(push_payload, base_branch="custom-branch")

    # Verify PR creation uses custom base branch
    mock_github_helper.repo.create_pull.assert_called_once_with(
        base="custom-branch",
        head=push_payload["ref"],
        title="Test commit",
        body="Created by FastGitHub",
        draft=True,
    )
