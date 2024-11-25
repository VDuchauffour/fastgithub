<p align="center">
  <a href="https://github.com/VDuchauffour/fastgithub">
    <img src="https://github.com/VDuchauffour/fastgithub/blob/main/assets/fastgithub.png?raw=true" alt="FastGithub written in white with a drawing of a bolt." width="45%" height="auto">
  </a>
</p>
  <p align="center" markdown=1>
    <i>A Python library to supercharge your GitHub organization with bots and webhooks. </i>
  </p>
  <p align="center" markdown=1>
    <a href="https://github.com/VDuchauffour/fastgithub/actions/workflows/ci.yml">
      <img src="https://github.com/VDuchauffour/fastgithub/actions/workflows/ci.yml/badge.svg" alt="CI Pipeline">
    </a>
    <a href="https://github.com/VDuchauffour/fastgithub/actions/workflows/release.yml">
      <img src="https://github.com/VDuchauffour/fastgithub/actions/workflows/release.yml/badge.svg" alt="Release">
    </a>
    <a href="https://codecov.io/gh/VDuchauffour/fastgithub">
      <img src="https://codecov.io/gh/VDuchauffour/fastgithub/branch/main/graph/badge.svg" alt="Codecov">
    </a>
    <br>
    <a href="https://github.com/astral-sh/ruff">
      <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json" alt="Ruff">
    </a>
    <a href="https://github.com/pre-commit/pre-commit">
      <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit" alt="Pre-commit">
    </a>
    <a href="https://spdx.org/licenses/">
      <img src="https://img.shields.io/github/license/VDuchauffour/fastgithub?color=blueviolet" alt="License">
    </a>
    <br>
    <a href="https://pypi.org/project/fastgithub/">
      <img src="https://img.shields.io/pypi/pyversions/fastgithub.svg?logo=python&label=Python&logoColor=gold" alt="PyPI - Python version">
    </a>
    <a href="https://pypi.org/project/fastgithub/">
      <img src="https://img.shields.io/pypi/v/fastgithub.svg?logo=pypi&label=PyPI&logoColor=gold" alt="PyPI - Version">
    </a>
  </p>
</p>
<hr>
    <p align="justify">
    <b>FastGitHub</b> is a Python package for <b>FastAPI</b>, offering a GitHub webhooks handler and easy Bot creation utilities, streamlined through <b>recipes</b> for easy operations on Github organizations and repositories.
    </p>
<p><b>More informations about Github webhooks and payloads</b>: <a href="https://docs.github.com/en/webhooks/webhook-events-and-payloads">docs.github.com/en/webhooks/webhook-events-and-payloads</a></p>
<hr>

## Features

- ⚙ **Seamless experience**: GitHub webhook handler and router classes that just works.
- ⚡️ **FastAPI native**: Build for FastAPI but can be easily integrate in any WSGI web application framework.
- 🔌 **Battery included**: Come with a set of builtins recipes for most common GitHub operations.
- ️⛏ **Modularity**: Recipes can be easily define for custom-tailor needs.

## Requirements

<p>Before installing FastGitHub, ensure you have the following prerequisites:</p>
<ul>
  <li><b>Python:</b> Version 3.12 or newer.</li>
  <li><b>FastAPI:</b> FastGitHub is built to work with FastAPI, so having FastAPI in your project is essential.</li>
</ul>

## ️️Installation

Install the package from the PyPI registry.

```shell
pip install fastgithub
```

## Usage

This is a basic example that handles the creation of a PR during a push event and the extraction of labels from the PR's commit messages.

```python
import os

import uvicorn
from fastapi import FastAPI
from github import Auth, Github

from fastgithub import GithubWebhookHandler, SignatureVerificationSHA256, webhook_router
from fastgithub.recipes.github import AutoCreatePullRequest, LabelsFromCommits

signature_verification = SignatureVerificationSHA256(secret="mysecret")  # noqa: S106
webhook_handler = GithubWebhookHandler(signature_verification)

github = Github(auth=Auth.Token(os.environ["GITHUB_TOKEN"]))

webhook_handler.listen("push", [AutoCreatePullRequest(github)])
webhook_handler.listen("pull_request", [LabelsFromCommits(github)])


app = FastAPI()
router = webhook_router(handler=webhook_handler, path="/postreceive")
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app)
```

You can define your own `Recipe` (or `GithubRecipe`) by inherit from these classes. A `Recipe` need a class attribute `events` that take a list of events to listen to, by default the recipe is listen by any type of event (ie. `*`).

The `webhook_router` uses the `__call__` method to perform the hooks.

```python
from collections.abc import Callable

from fastgithub import Recipe, GithubRecipe
from fastgithub.helpers.github import GithubHelper
from fastgithub.types import Payload


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
```

## Development

In order to install all development dependencies, run the following command:

```shell
uv sync
```

To ensure that you follow the development workflow, please setup the pre-commit hooks:

```shell
uv run pre-commit install
```

## Acknowledgements

- Initial ideas and designs were inspired by [python-github-webhook](https://github.com/bloomberg/python-github-webhook) and [python-github-bot-api](https://github.com/NiklasRosenstein/python-github-bot-api/).
- README.md layout was inspired by [FastCRUD](https://github.com/igorbenav/fastcrud).
