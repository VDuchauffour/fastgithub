from collections.abc import Callable

from fastgithub.helpers.github import GithubHelper
from fastgithub.recipes._base import GithubRecipe
from fastgithub.types import Payload

LABEL_CONFIG: dict[str, list[str]] = {
    "#nodraft": ["nodraft"],
    "#fast": ["nodraft", "automerge", "autoapprove"],
    "#release": ["nodraft", "automerge", "autorelease"],
    "#furious": ["nodraft", "automerge", "autoapprove", "autorelease"],
}


class LabelsFromCommits(GithubRecipe):
    @property
    def events(self) -> dict[str, Callable]:
        return {"pull_request": self._process_push}

    def _process_push(
        self,
        payload: Payload,
        labels_config: dict[str, list[str]] = LABEL_CONFIG,
    ):
        gh = GithubHelper(self.github, payload["repository"]["full_name"])
        if not gh.rate_status.too_low():
            pr = gh.repo.get_pull(payload["number"])
            if labels := gh.extract_labels_from_pr(pr, labels_config):
                gh.add_labels_to_pr(pr, labels)
