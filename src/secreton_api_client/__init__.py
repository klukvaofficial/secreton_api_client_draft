"""Secreton API Client - Python HTTP client for Secreton services."""

from ._version import __version__
from .auth import BearerAuth, SecretOnAuth
from .client import SyncSecretOnClient, AsyncSecretOnClient
from .exceptions import (
    APIClientError,
    AuthenticationError,
    HTTPError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)

__all__ = [
    "__version__",
    "SyncSecretOnClient",
    "AsyncSecretOnClient",
    "BearerAuth",
    "SecretOnAuth",
    "APIClientError",
    "AuthenticationError",
    "HTTPError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "ValidationError",
]
