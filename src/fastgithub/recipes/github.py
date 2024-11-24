from datetime import datetime

from github import Github
from github.GithubException import GithubException

from fastgithub.types import Payload

from ._base import Recipe


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
    def __init__(self, github: Github) -> None:
        self._github = github
        self._rate_status = RateStatus(self.github)

    @property
    def github(self) -> Github:
        return self._github

    @property
    def rate_status(self) -> RateStatus:
        return self._rate_status


class GithubBaseRecipe(Recipe):
    def __init__(self, github: Github) -> None:
        self.gh = GithubHelper(github)

    @property
    def github(self) -> Github:
        return self.gh.github

    @property
    def rate_status(self) -> RateStatus:
        return self.gh.rate_status

    def execute(self, payload: Payload):
        if not self.rate_status.too_low():
            pass


class AutoCreatePullRequest(GithubBaseRecipe):
    def execute(
        self,
        payload: Payload,
        base_branch: str | None = None,
        title: str | None = None,
        body: str = "Created by FastGitHub",
        as_draft: bool = False,
    ):
        repo = self.github.get_repo(payload["repository"]["full_name"])

        base_branch = base_branch or repo.default_branch
        head_branch = payload["ref"]
        _title = title or repo.get_commits(sha=head_branch)[0].commit.message
        try:
            repo.create_pull(
                base=base_branch,
                head=head_branch,
                title=_title,
                body=body,
                draft=as_draft,
            )
        except GithubException as ex:
            if ex.status != 422:
                raise ex
