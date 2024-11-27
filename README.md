<p align="center">
  <a href="https://github.com/VDuchauffour/fastgithub">
    <img src="https://github.com/VDuchauffour/fastgithub/blob/main/assets/fastgithub.png?raw=true" alt="FastGithub written in white with a drawing of a bolt." width="85%" height="auto">
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
- ⚡️ **FastAPI native**: Build for FastAPI but can be easily integrate with any WSGI web application framework.
- 🔌 **Battery included**: Come with a set of built-in recipes for the most common GitHub operations.
- ️⛏ **Modularity**: Recipes can be easily defined for tailor-made needs.

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

FastGitHub usually involves 3 steps to handle GitHub webhooks:

1. Define the recipes you want to use.
2. Attach these recipes to a `GithubWebhookHandler`.
3. Include a `webhook_router` in your FastAPI application.

### Recipes

To define a `Recipe` (or `GithubRecipe`), simply add `events` property that returns a `dict` with the events as keys and their methods to execute. Use `*` to trigger the recipe on any events.

To use a `GithubRecipe`, a `Github` instance from [PyGithub](https://github.com/PyGithub/PyGithub) is required when instantiating the class.

You can also use raw functions, although this is not the best solution.

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


def very_simple_recipe(payload: Payload) -> None:
    print(f"Hello from: {payload['repository']}")
```

#### Available recipes

- `AutoCreatePullRequest`: create a PR when a new branch is pushed.
- `LabelsFromCommits`: add label to a PR using commit messages (a default config is provided).

GitHub recipes can be imported from `fastgithub.recipes.github`.

### Webhook handler

Here's a basic example how to define a `GithubWebhookHandler` with SHA256 signature verification. Setting `signature_verification=None` allows you to use the handler without signature verification (which is not at all the recommended way to publish GitHub webhook).

```python
from fastgithub import GithubWebhookHandler, SignatureVerificationSHA256

signature_verification = SignatureVerificationSHA256(secret="mysecret")
webhook_handler = GithubWebhookHandler(signature_verification)
```

You can use the `plan` method to set recipes to a handler. The `listen` handler's method allows you attach recipe functions to specific events. The `listen` method can also be used as a decorator.

```python
webhook_handler.plan([Hello()])

webhook_handler.listen("pull_request", [very_simple_recipe])


@webhook_handler.listen("pull_request")
def another_simple_recipe(payload: Payload) -> None:
    print(f"Hello from: {payload['repository']}")
```

### Webhook router

The `webhook_router` function returns a `fastapi.APIRouter`. You can adopte the inner logic of this function to suit your needs.

```python
import uvicorn
from fastapi import FastAPI

from fastgithub import webhook_router

app = FastAPI()
router = webhook_router(handler=webhook_handler, path="/postreceive")
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app)
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
