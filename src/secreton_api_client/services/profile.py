"""Profile service for Secreton API."""

from typing import Optional
from uuid import UUID

import httpx

from ..http_client import HTTPClient
from ..models.profile import BalanceTopupResponse, UserProfile

class ProfileService:
    """Service for profile operations."""

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize profile service.

        Args:
            http_client: HTTP client instance
        """
        self.http_client = http_client
        self.endpoint_base = "/api/profile"

    async def get_profile(self, auth: httpx.Auth, user_id: Optional[UUID] = None) -> UserProfile:
        """Get user profile information.

        Args:
            auth: Authentication object
            user_id: Optional user ID (if not provided, returns current user)

        Returns:
            User profile data

        Raises:
            AuthenticationError: If not authorized
            NotFoundError: If user doesn't exist
        """
        endpoint = f"{self.endpoint_base}/profile"
        params = {}

        if user_id:
            params["user_id"] = str(user_id)

        response = await self.http_client.get(
            endpoint,
            auth=auth,
            params=params if params else None
        )
        return UserProfile(**response.json())

    async def topup_balance(
        self,
        amount: float,
        auth: httpx.Auth,
        user_id: Optional[UUID] = None
    ) -> BalanceTopupResponse:
        """Top up user balance.

        Args:
            amount: Amount to top up (minimum: 10)
            auth: Authentication object
            user_id: Optional user ID (if not provided, tops up current user)

        Returns:
            Balance top-up response with payment information

        Raises:
            ValueError: If amount is less than minimum
            AuthenticationError: If not authorized
        """
        if amount < 10:
            raise ValueError("Amount must be at least 10")

        endpoint = f"{self.endpoint_base}/topup"
        params = {"amount": amount}

        if user_id:
            params["user_id"] = str(user_id)

        response = await self.http_client.get(endpoint, auth=auth, params=params)
        return BalanceTopupResponse(**response.json())