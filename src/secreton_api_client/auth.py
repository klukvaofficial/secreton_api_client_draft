"""Authentication classes for Secreton API."""

import httpx


class BearerAuth(httpx.Auth):
    """Bearer token authentication for httpx."""

    def __init__(self, token: str) -> None:
        """Initialize bearer authentication.

        Args:
            token: Bearer token for authentication
        """
        self.token = token

    def auth_flow(self, request: httpx.Request):
        """Apply bearer token to request headers.

        Args:
            request: HTTP request to authenticate

        Yields:
            Authenticated request
        """
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


class SecretOnAuth(httpx.Auth):
    """Custom Secreton authentication using 'Auth' header."""

    def __init__(self, token: str) -> None:
        """Initialize Secreton authentication.

        Args:
            token: Authentication token
        """
        self.token = token

    def auth_flow(self, request: httpx.Request):
        """Apply Secreton auth token to request headers.

        Args:
            request: HTTP request to authenticate

        Yields:
            Authenticated request
        """
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request
