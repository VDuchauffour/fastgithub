"""Github quota helper."""

from abc import ABC
from collections.abc import Callable

from github import Github


class Recipe(ABC):
    @property
    def events(self) -> dict[str, Callable]:
        return {}


class GithubRecipe(Recipe):
    def __init__(self, github: Github) -> None:
        self.github = github
