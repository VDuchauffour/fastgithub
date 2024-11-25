import os
from collections.abc import Callable

import uvicorn
from fastapi import FastAPI
from github import Auth, Github

from fastgithub import (
    GithubRecipe,
    GithubWebhookHandler,
    Recipe,
    SignatureVerificationSHA256,
    webhook_router,
)
from fastgithub.helpers.github import GithubHelper
from fastgithub.types import Payload

signature_verification = SignatureVerificationSHA256(secret="mysecret")  # noqa: S106
webhook_handler = GithubWebhookHandler(signature_verification)

github = Github(auth=Auth.Token(os.environ["GITHUB_TOKEN"]))


class Hello(Recipe):
    @property
    def events(self) -> dict[str, Callable]:
        return {"*": self.__call__}

    def __call__(self, payload: Payload):
        print(f"Hello from: {payload['repository']}")


class MyGithubRecipe(GithubRecipe):
    @property
    def events(self) -> dict[str, Callable]:
        return {"push": self.__call__, "pull_request": self.__call__}

    def __call__(self, payload: Payload):
        gh = GithubHelper(self.github, repo_fullname=payload["repository"]["full_name"])
        if not gh.rate_status.too_low():
            print(f"Hello from {gh.repo.full_name}!")


recipes = [Hello(), MyGithubRecipe(github)]
webhook_handler.listen("push", recipes)

app = FastAPI()
router = webhook_router(handler=webhook_handler, path="/postreceive")
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app)
