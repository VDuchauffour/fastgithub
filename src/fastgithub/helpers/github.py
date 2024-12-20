from github import Github, RateLimitExceededException
from github.PullRequest import PullRequest
from github.RateLimit import RateLimit


class RateStatus:
    """A class that handle GiHub API rate limit status."""

    def __init__(self, github: Github, threshold: float = 0.5) -> None:
        self._github = github
        self.threshold = threshold
        self.status: RateLimit | None = None

    @property
    def github(self) -> Github:
        return self._github

    def reset(self) -> None:
        self.status = None

    def update(self) -> RateLimit:
        self.status = self.github.get_rate_limit()
        return self.status

    def available(self) -> float:
        """Return the available percent of the rate limit."""
        status = self.update()
        return status.core.remaining / status.core.limit if status.core.limit > 0 else 0.0

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

    def raise_for_rate_excess(self) -> None:
        if self.rate_status.too_low():
            status = self.rate_status.status
            assert isinstance(status, RateLimit)  # noqa: S101
            raise RateLimitExceededException(
                429,
                status.core.raw_data,
                status.core.raw_headers,  # type: ignore
            )

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
