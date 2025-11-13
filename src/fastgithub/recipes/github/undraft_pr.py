from collections.abc import Callable

from github import Github

from fastgithub.helpers.github import GithubHelper, Label
from fastgithub.recipes._base import GithubRecipe
from fastgithub.recipes.github._config import NODRAFT
from fastgithub.types import Payload


class UndraftPR(GithubRecipe):
    """
    Undraft a pull request when the draft label is removed.
    """

    def __init__(self, github: Github, draft_label: Label = NODRAFT):
        super().__init__(github)
        self.draft_label = draft_label

    @property
    def events(self) -> dict[str, Callable]:
        return {"pull_request": self._process_pull_request}

    def _process_pull_request(self, payload: Payload):
        gh = GithubHelper(self.github, payload["repository"]["full_name"])
        gh.raise_for_rate_excess()

        pr = gh.repo.get_pull(payload["number"])
        if (
            payload["action"] == "labeled"
            and payload["label"]["name"] == self.draft_label
            and self.draft_label in pr.labels
        ):
            pr.mark_ready_for_review()
        elif payload["action"] == "unlabeled" and payload["label"]["name"] == self.draft_label:
            pr.convert_to_draft()
