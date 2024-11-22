import os

from github import Auth, Github
from github.GithubException import GithubException


def autocreate_pull_request(
    data,
    log,
    base_branch: str | None = None,
    title: str | None = None,
    body: str = "Created by FastGitHub",
    as_draft: bool = False,
):
    auth = Auth.Token(os.environ["GITHUB_TOKEN"])
    github = Github(auth=auth)
    repo = github.get_repo(data["repository"]["full_name"])

    base_branch = base_branch or repo.default_branch
    head_branch = data["ref"]
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
        if ex.status == 422:
            log.info(
                "Couldn't create the PR",
                httpStatusCode=ex.status,
                httpResponseContent=ex.data,
                githubRepoName=repo.full_name,
            )
        else:
            raise ex
