"""Authentication service for Secreton API."""

from typing import Dict, Optional, Union
from uuid import UUID

import httpx

from ..http_client import HTTPClient
from ..models.auth import (
    LoginResponse,
    PasswordSetResponse,
    PhoneConfirmationResponse,
    RegisterResponse,
)

class AuthService:
    """Service for authentication operations."""

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize authentication service.

        Args:
            http_client: HTTP client instance
        """
        self.http_client = http_client
        self.endpoint_base = "/api/auth"

    async def login(self, phone: int) -> RegisterResponse:
        """Initiate login process with phone number.

        Args:
            phone: Phone number for login

        Returns:
            Login response with request_id

        Raises:
            ValidationError: If phone number is invalid
            APIClientError: If request fails
        """
        if not (79000000000 <= phone <= 79999999999):
            raise ValueError("Phone number must be between 79000000000 and 79999999999")

        endpoint = f"{self.endpoint_base}/login"
        data = {"phone": phone}

        response = await self.http_client.post(endpoint, json_data=data)
        return RegisterResponse(**response.json())

    async def password_login(self, phone: int, password: str) -> LoginResponse:
        """Login with phone and password.

        Args:
            phone: Phone number
            password: User password

        Returns:
            Login response with token

        Raises:
            AuthenticationError: If credentials are invalid
            ValidationError: If phone number is invalid
        """
        if not (70000000000 <= phone <= 79999999999):
            raise ValueError("Phone number must be between 70000000000 and 79999999999")

        endpoint = f"{self.endpoint_base}/password_login"
        data = {"phone": phone, "password": password}

        response = await self.http_client.post(endpoint, json_data=data)
        return LoginResponse(**response.json())

    async def phone_confirmation(
        self,
        request_id: Union[str, UUID],
        code: int
    ) -> PhoneConfirmationResponse:
        """Confirm phone number with SMS code.

        Args:
            request_id: Request ID from login response
            code: SMS confirmation code (0-9999)

        Returns:
            Phone confirmation response

        Raises:
            ValidationError: If code is invalid
            AuthenticationError: If confirmation fails
        """
        if not (0 <= code <= 9999):
            raise ValueError("Code must be between 0 and 9999")

        endpoint = f"{self.endpoint_base}/phone_confirmation"
        data = {"request_id": str(request_id), "code": code}

        response = await self.http_client.post(endpoint, json_data=data)
        return PhoneConfirmationResponse(**response.json())

    async def set_password(
        self,
        request_id: Union[str, UUID],
        password: str
    ) -> PasswordSetResponse:
        """Set password after phone confirmation.

        Args:
            request_id: Request ID from login response
            password: New password to set

        Returns:
            Password set response with token

        Raises:
            ValidationError: If password is invalid
            AuthenticationError: If request_id is invalid
        """
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")

        endpoint = f"{self.endpoint_base}/password"
        data = {"request_id": str(request_id), "password": password}

        response = await self.http_client.post(endpoint, json_data=data)
        return PasswordSetResponse(**response.json())

    async def send_code(self, request_id: Union[str, UUID]) -> Dict:
        """Resend SMS confirmation code.

        Args:
            request_id: Request ID from login response

        Returns:
            Code sending response

        Raises:
            AuthenticationError: If request_id is invalid
            RateLimitError: If too many requests
        """
        endpoint = f"{self.endpoint_base}/send_code"
        data = {"request_id": str(request_id)}

        response = await self.http_client.post(endpoint, json_data=data)
        return response.json()

    async def logout(self, auth: httpx.Auth) -> Dict:
        """Logout current user.

        Args:
            auth: Authentication object with valid token

        Returns:
            Logout response

        Raises:
            AuthenticationError: If token is invalid
        """
        endpoint = f"{self.endpoint_base}/logout"

        response = await self.http_client.post(endpoint, auth=auth)
        return response.json()