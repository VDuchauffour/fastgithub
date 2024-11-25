from collections.abc import Callable

from github.GithubException import GithubException

from fastgithub.helpers.github import GithubHelper
from fastgithub.recipes._base import GithubRecipe
from fastgithub.types import Payload


class AutoCreatePullRequest(GithubRecipe):
    @property
    def events(self) -> dict[str, Callable]:
        return {"push": self._process_push}

    def _process_push(
        self,
        payload: Payload,
        base_branch: str | None = None,
        title: str | None = None,
        body: str = "Created by FastGitHub",
        as_draft: bool = False,
    ):
        gh = GithubHelper(self.github, repo_fullname=payload["repository"]["full_name"])
        if not gh.rate_status.too_low():
            base_branch = base_branch or gh.repo.default_branch
            head_branch = payload["ref"]
            _title = title or gh.repo.get_commits(sha=head_branch)[0].commit.message
            try:
                gh.repo.create_pull(
                    base=base_branch,
                    head=head_branch,
                    title=_title,
                    body=body,
                    draft=as_draft,
                )
            except GithubException as ex:
                if ex.status != 422:
                    raise ex
