import re

import github
import github.Label
from github import Github, RateLimitExceededException
from github.PullRequest import PullRequest
from github.RateLimitOverview import RateLimitOverview
from pydantic import BaseModel


class Label(BaseModel):
    """A data model for GitHub label."""

    name: str
    color: str
    description: str


class RateStatus:
    """A class that handle GiHub API rate limit status."""

    def __init__(self, github: Github, threshold: float = 0.5) -> None:
        self._github = github
        self.threshold = threshold
        self.status: RateLimitOverview | None = None

    @property
    def github(self) -> Github:
        return self._github

    def reset(self) -> None:
        self.status = None

    def update(self) -> RateLimitOverview:
        self.status = self.github.get_rate_limit()
        return self.status

    def available(self) -> float:
        """Return the available percent of the rate limit."""
        status = self.update()
        return (
            status.resources.core.remaining / status.resources.core.limit
            if status.resources.core.limit > 0
            else 0.0
        )

    def too_low(self) -> bool:
        """Return if the rate limit is too short."""
        return self.available() < self.threshold


class GithubHelper:
    LABEL_REGEX = re.compile(r"#([a-z][a-z1-9-]+)([^a-z1-9-]|$)")

    def __init__(self, github: Github, repo_fullname: str, rate_threshold: float = 0.5) -> None:
        self._github = github
        self._rate_status = RateStatus(github, rate_threshold)
        self.repo = github.get_repo(repo_fullname, lazy=True)

    @property
    def rate_status(self) -> RateStatus:
        return self._rate_status

    def raise_for_rate_excess(self) -> None:
        if self.rate_status.too_low():
            status: RateLimitOverview = self.rate_status.status  # type: ignore
            raise RateLimitExceededException(
                429,
                status.resources.core.raw_data,
                status.resources.core.raw_headers,  # type: ignore
            )

    def _get_or_create_label(
        self,
        name: str,
        color: str = "ff66cc",
        description: str = "Created by FastGitHub",
    ) -> github.Label.Label:
        """Fetch an existing label or create it."""
        try:
            label = self.repo.get_label(name)
        except github.UnknownObjectException:
            label = None

        if not label:
            label = self.repo.create_label(
                name=name,
                color=color,
                description=description,
            )
        return label

    @staticmethod
    def validate_label_name(name: str, pattern: re.Pattern) -> None:
        """Validate the name of a label given a regex pattern."""
        if not pattern.fullmatch(name):
            raise ValueError(
                f"The pattern `{name}` don't follow the regex {GithubHelper.LABEL_REGEX.pattern}!"
            )

    def extract_labels_from_commit(
        self, message: str, labels_config: dict[str, list[Label]]
    ) -> set[str]:
        """Extract labels from a commit message and create labels in the repo if needed."""
        labels = set()
        for pattern, labels_ in labels_config.items():
            self.__class__.validate_label_name(pattern, GithubHelper.LABEL_REGEX)
            if pattern in message:
                for label_ in labels_:
                    label_ = self._get_or_create_label(**label_.model_dump())
                    labels.update([label_.name])
        return labels

    def extract_labels_from_pr(
        self, pr: PullRequest, labels_config: dict[str, list[Label]]
    ) -> set[str]:
        """Extract labels from a PR and create labels in the repo if needed."""
        labels = set()
        commit_messages = [c.commit.message for c in pr.get_commits()]
        for message in commit_messages:
            labels = labels.union(self.extract_labels_from_commit(message, labels_config))
        return labels

    @staticmethod
    def add_labels_to_pr(pr: PullRequest, labels: set[str]):
        """Add a set of labels to a PR associated with a branch"""
        existing_labels = [lbl.name for lbl in pr.labels]
        new_labels = labels.difference(existing_labels)
        if not new_labels:
            return
        pr.add_to_labels(*new_labels)
