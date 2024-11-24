"""Github quota helper."""

from abc import ABC

from fastgithub.types import Payload


class Recipe(ABC):
    def execute(self, payload: Payload) -> None:
        raise NotImplementedError
