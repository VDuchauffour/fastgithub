from datetime import datetime

from github import Github
from github.PullRequest import PullRequest


class RateStatus:
    """A class that handle GiHub API rate limit status."""

    def __init__(self, github: Github, threshold: float = 0.5) -> None:
        self._github = github
        self.threshold = threshold

    @property
    def github(self) -> Github:
        return self._github

    def __str__(self):
        return (
            f"Rate Limit: {self.limit}, Rate Remaining: {self.remaining}, Rate Reset: {self.reset}"
        )

    @property
    def remaining(self) -> float:
        return self.github.get_rate_limit().core.remaining

    @property
    def limit(self) -> float:
        return self.github.get_rate_limit().core.limit

    @property
    def reset(self) -> datetime:
        return self.github.get_rate_limit().core.reset

    def available(self) -> float:
        """Return the available percent of the rate limit."""
        return self.remaining / self.limit if self.limit > 0 else 0.0

    def too_low(self) -> bool:
        """Return if the rate limit is too short."""
        return self.available() < self.threshold


class GithubHelper:
    def __init__(self, github: Github, repo_fullname: str, rate_threshold: float = 0.5) -> None:
        self._github = github
        self._rate_status = RateStatus(self.github, rate_threshold)
        self.repo = github.get_repo(repo_fullname, lazy=True)

    @property
    def github(self) -> Github:
        return self._github

    @property
    def rate_status(self) -> RateStatus:
        return self._rate_status

    @staticmethod
    def extract_labels_from_pr(pr: PullRequest, labels_config: dict[str, list[str]]) -> set[str]:
        labels = set()
        commit_messages = [c.commit.message for c in pr.get_commits()]
        for message in commit_messages:
            for pattern, labels_ in labels_config.items():
                if pattern in message:
                    labels.update(labels_)
        return labels

    @staticmethod
    def add_labels_to_pr(pr: PullRequest, labels: set[str]):
        """Add a set of labels to a PR associated with a branch"""
        existing_labels = [lbl.name for lbl in pr.labels]
        new_labels = labels.difference(existing_labels)
        if not new_labels:
            return
        pr.add_to_labels(*new_labels)
