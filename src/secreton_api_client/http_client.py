"""Base HTTP client for Secreton API."""

import logging
from typing import Any, Dict, Optional, Union

import httpx

from .exceptions import (
    APIClientError,
    AuthenticationError,
    HTTPError,
    NotFoundError,
    RateLimitError,
    RequestError,
    ServerError,
    ValidationError,
)

logger = logging.getLogger(__name__)

class HTTPClient:
    """Low-level HTTP client for API communication."""

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        verify_ssl: bool = True,
        user_agent: Optional[str] = None,
    ) -> None:
        """Initialize HTTP client.

        Args:
            base_url: Base URL of the API service
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            user_agent: Custom user agent string
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        # Setup default headers
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if user_agent:
            headers["User-Agent"] = user_agent

        # Initialize httpx client
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=httpx.Timeout(self.timeout),
            verify=self.verify_ssl,
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close HTTP client connection."""
        await self._client.aclose()

    async def request(
        self,
        method: str,
        endpoint: str,
        auth: Optional[httpx.Auth] = None,
        json_data: Optional[Dict[str, Any]] = None,
        form_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Make HTTP request with comprehensive error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            auth: Authentication object
            json_data: JSON data for request body
            form_data: Form data for request body
            files: Files for multipart upload
            params: URL query parameters
            headers: Additional headers

        Returns:
            HTTP response object

        Raises:
            APIClientError: For various API and network errors
        """
        url = endpoint if endpoint.startswith('http') else f"{self.base_url}{endpoint}"

        logger.debug(f"Making {method} request to {url}")

        try:
            # Prepare request arguments
            request_kwargs = {
                "method": method,
                "url": url,
                "auth": auth,
                "params": params,
                "timeout": self.timeout,
            }

            # Add headers if provided
            if headers:
                request_kwargs["headers"] = headers

            # Handle different data types
            if files:
                # Multipart form data with files
                request_kwargs["files"] = files
                if form_data:
                    request_kwargs["data"] = form_data
            elif form_data:
                # Form data only
                request_kwargs["data"] = form_data
                request_kwargs["headers"] = {"Content-Type": "application/x-www-form-urlencoded"}
            elif json_data:
                # JSON data
                request_kwargs["json"] = json_data

            # Make the request
            response = await self._client.request(**request_kwargs)

            # Handle response errors
            self._handle_response_errors(response)

            logger.debug(f"Request successful: {response.status_code}")
            return response

        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            raise RequestError(f"Request failed: {str(e)}")

        except httpx.TimeoutException as e:
            logger.error(f"Request timed out: {e}")
            raise RequestError(f"Request timed out: {str(e)}")

    def _handle_response_errors(self, response: httpx.Response) -> None:
        """Handle HTTP response errors.

        Args:
            response: HTTP response to check

        Raises:
            Specific APIClientError subclasses based on status code
        """
        if response.is_success:
            return

        status_code = response.status_code

        # Try to extract error message from response
        try:
            error_data = response.json()
            message = self._extract_error_message(error_data)
        except Exception:
            message = response.text or f"HTTP {status_code} error"

        logger.error(f"API error {status_code}: {message}")

        # Raise specific exceptions based on status code
        if status_code == 401:
            raise AuthenticationError(message, status_code)
        elif status_code == 403:
            raise AuthenticationError(message, status_code)  # Treat as auth error
        elif status_code == 404:
            raise NotFoundError(message, status_code)
        elif status_code == 422:
            validation_errors = self._extract_validation_errors(error_data)
            raise ValidationError(message, status_code, validation_errors)
        elif status_code == 429:
            retry_after = self._extract_retry_after(response.headers)
            raise RateLimitError(message, status_code, retry_after)
        elif status_code >= 500:
            raise ServerError(message, status_code)
        else:
            raise HTTPError(message, status_code)

    def _extract_error_message(self, error_data: Dict[str, Any]) -> str:
        """Extract error message from response data."""
        if isinstance(error_data.get("detail"), str):
            return error_data["detail"]
        elif isinstance(error_data.get("detail"), list) and error_data["detail"]:
            return error_data["detail"][0].get("msg", "API error")
        elif error_data.get("message"):
            return error_data["message"]
        else:
            return "Unknown API error"

    def _extract_validation_errors(self, error_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract validation errors from response data."""
        validation_errors = {}
        try:
            if isinstance(error_data.get("detail"), list):
                for error in error_data["detail"]:
                    field = ".".join(str(x) for x in error.get("loc", []))
                    validation_errors[field] = error.get("msg", "Invalid value")
        except Exception:
            pass
        return validation_errors

    def _extract_retry_after(self, headers: httpx.Headers) -> Optional[int]:
        """Extract retry-after value from headers."""
        try:
            return int(headers.get("Retry-After", 0))
        except (ValueError, TypeError):
            return None

    async def get(
        self,
        endpoint: str,
        auth: Optional[httpx.Auth] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Make GET request.

        Args:
            endpoint: API endpoint
            auth: Authentication
            params: Query parameters
            headers: Additional headers

        Returns:
            HTTP response
        """
        return await self.request("GET", endpoint, auth=auth, params=params, headers=headers)

    async def post(
        self,
        endpoint: str,
        auth: Optional[httpx.Auth] = None,
        json_data: Optional[Dict[str, Any]] = None,
        form_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Make POST request.

        Args:
            endpoint: API endpoint
            auth: Authentication
            json_data: JSON payload
            form_data: Form data payload
            files: Files for upload
            headers: Additional headers

        Returns:
            HTTP response
        """
        return await self.request(
            "POST",
            endpoint,
            auth=auth,
            json_data=json_data,
            form_data=form_data,
            files=files,
            headers=headers
        )

    async def delete(
        self,
        endpoint: str,
        auth: Optional[httpx.Auth] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Make DELETE request.

        Args:
            endpoint: API endpoint
            auth: Authentication
            json_data: JSON payload
            headers: Additional headers

        Returns:
            HTTP response
        """
        return await self.request("DELETE", endpoint, auth=auth, json_data=json_data, headers=headers)