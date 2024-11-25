"""Github quota helper."""

from abc import ABC

from github import Github

from fastgithub.types import Payload


class Recipe(ABC):
    events = ["*"]

    def __call__(self, payload: Payload) -> None:
        raise NotImplementedError


class GithubRecipe(Recipe):
    def __init__(self, github: Github) -> None:
        self.github = github
