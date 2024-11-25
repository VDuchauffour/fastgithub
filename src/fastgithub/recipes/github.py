from github.GithubException import GithubException

from fastgithub.helpers.github import GithubHelper
from fastgithub.types import Payload

from ._base import GithubRecipe


class AutoCreatePullRequest(GithubRecipe):
    def __call__(
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


LABEL_CONFIG: dict[str, list[str]] = {
    "#nodraft": ["nodraft"],
    "#fast": ["nodraft", "automerge", "autoapprove"],
    "#release": ["nodraft", "automerge", "autorelease"],
    "#furious": ["nodraft", "automerge", "autoapprove", "autorelease"],
}


class LabelFromCommit(GithubRecipe):
    def __call__(
        self,
        payload: Payload,
        labels_config: dict[str, list[str]] = LABEL_CONFIG,
    ):
        gh = GithubHelper(self.github, payload["repository"]["full_name"])
        if not gh.rate_status.too_low():
            pr = gh.repo.get_pull(payload["number"])
            if labels := gh.extract_labels_from_pr(pr, labels_config):
                gh.add_labels_to_pr(pr, labels)
