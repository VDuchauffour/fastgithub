"""FastGitHub."""

from importlib.metadata import version

from .endpoint.webhook_router import webhook_router
from .handler import GithubWebhookHandler
from .signature import SignatureVerificationSHA1, SignatureVerificationSHA256

__version__ = version("fastgithub")
