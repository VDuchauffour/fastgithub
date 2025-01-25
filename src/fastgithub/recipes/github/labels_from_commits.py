from collections.abc import Callable

from github import Github

from fastgithub.helpers.github import GithubHelper, Label
from fastgithub.recipes._base import GithubRecipe
from fastgithub.types import Payload

from ._config import LABEL_CONFIG


class LabelsFromCommits(GithubRecipe):
    def __init__(
        self, github: Github, labels_config: dict[str, list[Label]] = LABEL_CONFIG
    ) -> None:
        super().__init__(github)
        self.labels_config = labels_config

    @property
    def events(self) -> dict[str, Callable]:
        return {"pull_request": self._process_push}

    def _process_push(self, payload: Payload):
        gh = GithubHelper(self.github, payload["repository"]["full_name"])
        gh.raise_for_rate_excess()

        pr = gh.repo.get_pull(payload["number"])
        if labels := gh.extract_labels_from_pr(pr, self.labels_config):
            gh.add_labels_to_pr(pr, labels)
