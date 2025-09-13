"""Main Secreton API client."""

import logging
from typing import Optional

from ._version import __version__
from .auth import SecretOnAuth
from .http_client import HTTPClient
from .services import AuthService, OrdersService, ProfileService

logger = logging.getLogger(__name__)


class SecretOnClient:
    """Main client for Secreton API.

    This is the primary interface for interacting with the Secreton API.
    It provides access to all service endpoints through a unified interface.

    Example:
        async with SecretOnClient("https://api.secreton.ru") as client:
            # Login
            login_resp = await client.auth.login(phone=79123456789)

            # Set token after authentication
            client.set_token("your-auth-token")

            # Use authenticated services
            profile = await client.profile.get_profile()
    """

    def __init__(
        self,
        base_url: str,
        token: Optional[str] = None,
        timeout: float = 30.0,
        verify_ssl: bool = True,
        user_agent: Optional[str] = None,
    ) -> None:
        """Initialize Secreton API client.

        Args:
            base_url: Base URL of the Secreton API service
            token: Optional authentication token
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            user_agent: Custom user agent string
        """
        self.base_url = base_url
        self.token = token

        # Initialize HTTP client
        self.http_client = HTTPClient(
            base_url=base_url,
            timeout=timeout,
            verify_ssl=verify_ssl,
            user_agent=user_agent or f"secreton-api-client/{__version__}",
        )

        # Initialize authentication object
        self._auth = SecretOnAuth(token) if token else None

        # Initialize services
        self.auth = AuthService(self.http_client)

        # Initialize authenticated services if token is provided
        if self.token:
            self._init_authenticated_services()

        logger.info(f"Initialized Secreton client for {base_url}")

    def _init_authenticated_services(self) -> None:
        """Initialize services that require authentication."""
        self.profile = ProfileService(self.http_client)
        self.orders = OrdersService(self.http_client)

    def set_token(self, token: str) -> None:
        """Set or update authentication token.

        Args:
            token: Authentication token to use for requests

        Note:
            After setting a token, authenticated services become available:
            - client.profile: Profile operations
            - client.orders: Order operations
        """
        self.token = token
        self._auth = SecretOnAuth(token)

        # Initialize authenticated services
        self._init_authenticated_services()

        logger.info("Authentication token updated")

    def get_auth(self) -> Optional[SecretOnAuth]:
        """Get current authentication object.

        Returns:
            Authentication object or None if no token is set
        """
        return self._auth

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close HTTP client connection.

        This should be called when you're done using the client
        to properly close the underlying HTTP connection.
        """
        await self.http_client.close()
        logger.info("Secreton client closed")


class AsyncSecretOnClient:
    """Async client for Secreton API.

    This is the primary interface for interacting with the Secreton API.
    It provides access to all service endpoints through a unified interface.

    Example:
        async with SecretOnClient("https://api.secreton.ru") as client:
            # Login
            login_resp = await client.auth.login(phone=79123456789)

            # Set token after authentication
            client.set_token("your-auth-token")

            # Use authenticated services
            profile = await client.profile.get_profile()
    """

    def __init__(
        self,
        base_url: str,
        token: Optional[str] = None,
        timeout: float = 30.0,
        verify_ssl: bool = True,
        user_agent: Optional[str] = None,
    ) -> None:
        """Initialize Secreton API client.

        Args:
            base_url: Base URL of the Secreton API service
            token: Optional authentication token
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            user_agent: Custom user agent string
        """
        self.base_url = base_url
        self.token = token

        # Initialize HTTP client
        self.http_client = HTTPClient(
            base_url=base_url,
            timeout=timeout,
            verify_ssl=verify_ssl,
            user_agent=user_agent or f"secreton-api-client/{__version__}",
        )

        # Initialize authentication object
        self._auth = SecretOnAuth(token) if token else None

        # Initialize services
        self.auth = AuthService(self.http_client)

        # Initialize authenticated services if token is provided
        if self.token:
            self._init_authenticated_services()

        logger.info(f"Initialized Secreton client for {base_url}")

    def _init_authenticated_services(self) -> None:
        """Initialize services that require authentication."""
        self.profile = ProfileService(self.http_client)
        self.orders = OrdersService(self.http_client)

    def set_token(self, token: str) -> None:
        """Set or update authentication token.

        Args:
            token: Authentication token to use for requests

        Note:
            After setting a token, authenticated services become available:
            - client.profile: Profile operations
            - client.orders: Order operations
        """
        self.token = token
        self._auth = SecretOnAuth(token)

        # Initialize authenticated services
        self._init_authenticated_services()

        logger.info("Authentication token updated")

    def get_auth(self) -> Optional[SecretOnAuth]:
        """Get current authentication object.

        Returns:
            Authentication object or None if no token is set
        """
        return self._auth

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close HTTP client connection.

        This should be called when you're done using the client
        to properly close the underlying HTTP connection.
        """
        await self.http_client.close()
        logger.info("Secreton client closed")
