"""Exception classes for Secreton API Client."""

from typing import Any, Dict, Optional


class APIClientError(Exception):
    """Base exception for all API client errors."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        """Initialize API client error.

        Args:
            message: Error message
            status_code: HTTP status code if applicable
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self) -> str:
        """String representation of the error."""
        if self.status_code:
            return f"API Error {self.status_code}: {self.message}"
        return f"API Error: {self.message}"


class HTTPError(APIClientError):
    """Generic HTTP error for non-specific status codes."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        """Initialize HTTP error.

        Args:
            message: Error message
            status_code: HTTP status code
        """
        super().__init__(message, status_code)


class AuthenticationError(APIClientError):
    """Authentication failed (401, 403)."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        """Initialize authentication error.

        Args:
            message: Error message
            status_code: HTTP status code (typically 401 or 403)
        """
        super().__init__(message, status_code)


class PermissionError(APIClientError):
    """Permission denied (403)."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        """Initialize permission error.

        Args:
            message: Error message
            status_code: HTTP status code (typically 403)
        """
        super().__init__(message, status_code)


class NotFoundError(APIClientError):
    """Resource not found (404)."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        """Initialize not found error.

        Args:
            message: Error message
            status_code: HTTP status code (typically 404)
        """
        super().__init__(message, status_code)


class ValidationError(APIClientError):
    """Request validation failed (422)."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        validation_errors: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize validation error.

        Args:
            message: Error message
            status_code: HTTP status code (typically 422)
            validation_errors: Dictionary of field-specific validation errors
        """
        super().__init__(message, status_code)
        self.validation_errors = validation_errors or {}

    def __str__(self) -> str:
        """String representation including validation details."""
        base_str = super().__str__()
        if self.validation_errors:
            errors_str = ", ".join(
                [f"{field}: {error}" for field, error in self.validation_errors.items()]
            )
            return f"{base_str} (Validation errors: {errors_str})"
        return base_str


class RateLimitError(APIClientError):
    """Rate limit exceeded (429)."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        retry_after: Optional[int] = None,
    ) -> None:
        """Initialize rate limit error.

        Args:
            message: Error message
            status_code: HTTP status code (typically 429)
            retry_after: Seconds to wait before retrying
        """
        super().__init__(message, status_code)
        self.retry_after = retry_after

    def __str__(self) -> str:
        """String representation including retry information."""
        base_str = super().__str__()
        if self.retry_after:
            return f"{base_str} (Retry after {self.retry_after} seconds)"
        return base_str


class ServerError(APIClientError):
    """Server error (5xx)."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        """Initialize server error.

        Args:
            message: Error message
            status_code: HTTP status code (5xx range)
        """
        super().__init__(message, status_code)


class RequestError(APIClientError):
    """Request failed (network, timeout, etc.)."""

    def __init__(
        self, message: str, original_error: Optional[Exception] = None
    ) -> None:
        """Initialize request error.

        Args:
            message: Error message
            original_error: Original exception that caused this error
        """
        super().__init__(message)
        self.original_error = original_error

    def __str__(self) -> str:
        """String representation including original error."""
        base_str = super().__str__()
        if self.original_error:
            return f"{base_str} (Original: {self.original_error})"
        return base_str


class TimeoutError(RequestError):
    """Request timed out."""

    def __init__(self, message: str, timeout_duration: Optional[float] = None) -> None:
        """Initialize timeout error.

        Args:
            message: Error message
            timeout_duration: Timeout duration in seconds
        """
        super().__init__(message)
        self.timeout_duration = timeout_duration

    def __str__(self) -> str:
        """String representation including timeout duration."""
        base_str = super().__str__()
        if self.timeout_duration:
            return f"{base_str} (Timeout: {self.timeout_duration}s)"
        return base_str


class ConnectionError(RequestError):
    """Connection failed."""

    def __init__(self, message: str, host: Optional[str] = None) -> None:
        """Initialize connection error.

        Args:
            message: Error message
            host: Host that failed to connect to
        """
        super().__init__(message)
        self.host = host

    def __str__(self) -> str:
        """String representation including host information."""
        base_str = super().__str__()
        if self.host:
            return f"{base_str} (Host: {self.host})"
        return base_str


class FileError(APIClientError):
    """File operation error."""

    def __init__(self, message: str, file_path: Optional[str] = None) -> None:
        """Initialize file error.

        Args:
            message: Error message
            file_path: Path to the file that caused the error
        """
        super().__init__(message)
        self.file_path = file_path

    def __str__(self) -> str:
        """String representation including file path."""
        base_str = super().__str__()
        if self.file_path:
            return f"{base_str} (File: {self.file_path})"
        return base_str


# Exception mapping for HTTP status codes
HTTP_EXCEPTION_MAP = {
    400: ValidationError,
    401: AuthenticationError,
    403: PermissionError,
    404: NotFoundError,
    422: ValidationError,
    429: RateLimitError,
    500: ServerError,
    502: ServerError,
    503: ServerError,
    504: ServerError,
}


def get_exception_for_status_code(status_code: int) -> type:
    """Get appropriate exception class for HTTP status code.

    Args:
        status_code: HTTP status code

    Returns:
        Exception class for the given status code
    """
    if status_code in HTTP_EXCEPTION_MAP:
        return HTTP_EXCEPTION_MAP[status_code]
    elif 400 <= status_code < 500:
        return HTTPError
    elif 500 <= status_code < 600:
        return ServerError
    else:
        return APIClientError


def create_exception_from_response(
    status_code: int, message: str, response_data: Optional[Dict[str, Any]] = None
) -> APIClientError:
    """Create appropriate exception from HTTP response.

    Args:
        status_code: HTTP status code
        message: Error message
        response_data: Response data dictionary

    Returns:
        Appropriate exception instance
    """
    exception_class = get_exception_for_status_code(status_code)

    # Handle special cases with additional data
    if status_code == 422 and response_data:
        validation_errors = {}
        if isinstance(response_data.get("detail"), list):
            for error in response_data["detail"]:
                field = ".".join(str(x) for x in error.get("loc", []))
                validation_errors[field] = error.get("msg", "Invalid value")
        return ValidationError(message, status_code, validation_errors)

    elif status_code == 429 and response_data:
        retry_after = response_data.get("retry_after")
        return RateLimitError(message, status_code, retry_after)

    else:
        return exception_class(message, status_code)
