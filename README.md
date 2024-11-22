<div align="center">

# FastGitHub

<table>
  <tr>
    <td>
    </td>
    <td>
    </td>
  </tr>
  <tr>
    <td>
      CI/CD
    </td>
    <td>
      <a href="https://github.com/VDuchauffour/fastgithub/actions/workflows/ci.yml">
        <img src="https://github.com/VDuchauffour/fastgithub/actions/workflows/ci.yml/badge.svg" alt="CI Pipeline">
      </a>
      <a href="https://github.com/VDuchauffour/fastgithub/actions/workflows/release.yml">
        <img src="https://github.com/VDuchauffour/fastgithub/actions/workflows/release.yml/badge.svg" alt="Release">
      </a>
      <a href="https://interrogate.readthedocs.io/en/latest/">
        <img src=".github/assets/badges/interrogate_badge.svg" alt="Interrogate">
      </a>
      <a href="https://codecov.io/gh/VDuchauffour/fastgithub">
        <img src="https://codecov.io/gh/VDuchauffour/fastgithub/branch/main/graph/badge.svg" alt="Codecov">
      </a>
    </td>
  </tr>
  <tr>
    <td>
        Meta
    </td>
    <td>
      <a href="https://github.com/astral-sh/ruff">
        <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json" alt="Ruff">
      </a>
      <a href="https://github.com/pre-commit/pre-commit">
        <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit" alt="Pre-commit">
      </a>
      <a href="https://spdx.org/licenses/">
        <img src="https://img.shields.io/github/license/VDuchauffour/fastgithub?color=blueviolet" alt="License">
      </a>
    </td>
  </tr>
  <tr>
    <td>
        Package
    </td>
    <td>
      <a href="https://pypi.org/project/fastgithub/">
        <img src="https://img.shields.io/pypi/pyversions/fastgithub.svg?logo=python&label=Python&logoColor=gold" alt="PyPI - Python version">
      </a>
      <a href="https://pypi.org/project/fastgithub/">
        <img src="https://img.shields.io/pypi/v/fastgithub.svg?logo=pypi&label=PyPI&logoColor=gold" alt="PyPI - Version">
      </a>
    </td>
  </tr>
</table>

</div>

______________________________________________________________________

## About this project

FastGitHub provides a GitHub webhooks handler for FastAPI to automate your workflows.

FastGitHub also provides sets of automations (named _recipes_).

## ️️⚙️ Installation

Install the package from the PyPI registry.

```shell
pip install fastgithub
```

## ⚡ Usage

### Example

```python
from typing import Any
from fastapi import FastAPI
import uvicorn
from fastgithub.endpoint.webhook_router import webhook_router
from fastgithub.recipes.github import autocreate_pull_request
from fastgithub.webhook import GithubWebhookHandler

webhook_handler = GithubWebhookHandler(
    token="your-secret-token"
)  # by default os.environ["GITHUB_TOKEN"]


@webhook_handler.listen("push")
def hello(data: dict[str, Any]):
    print(f"Hello from: {data["repository"]}")


app = FastAPI()
router = webhook_router(handler=webhook_handler, path="/postreceive")
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app)
```

You can also fill a list of functions for a specific event to the handler:

```python
def hello(data: dict[str, Any]):
    print(f"Hello from: {data["repository"]}")


def bye(data: dict[str, Any]):
    print(f"Goodbye from: {data["repository"]}")


webhook_handler.listen("push", [hello, bye])
```

## ⛏️ Development

In order to install all development dependencies, run the following command:

```shell
uv sync
```

To ensure that you follow the development workflow, please setup the pre-commit hooks:

```shell
uv run pre-commit install
```
