"""FastGitHub."""

from importlib.metadata import version

from .endpoint.webhook_router import webhook_router
from .webhook.handler import GithubWebhookHandler
from .webhook.signature import SignatureVerificationSHA256

__version__ = version("fastgithub")
