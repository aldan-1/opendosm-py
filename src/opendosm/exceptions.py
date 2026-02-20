"""Custom exceptions for the OpenDOSM SDK."""

from __future__ import annotations

from typing import Any


class OpenDOSMError(Exception):
    """Base exception for all OpenDOSM SDK errors."""

    def __init__(self, message: str = "An error occurred with the OpenDOSM API") -> None:
        self.message = message
        super().__init__(self.message)


class APIError(OpenDOSMError):
    """Raised when the API returns an error response.

    Attributes:
        status_code: HTTP status code returned by the API.
        errors: List of error messages from the API response.
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        errors: list[Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.errors = errors or []
        super().__init__(message)

    def __str__(self) -> str:
        base = f"[{self.status_code}] {self.message}"
        if self.errors:
            details = "; ".join(str(e) for e in self.errors)
            return f"{base} — {details}"
        return base


class RateLimitError(APIError):
    """Raised when the API rate limit is exceeded (HTTP 429).

    Attributes:
        retry_after: Seconds to wait before retrying, if provided by the API.
    """

    def __init__(
        self,
        retry_after: float | None = None,
        errors: list[Any] | None = None,
    ) -> None:
        self.retry_after = retry_after
        super().__init__(
            message="Rate limit exceeded. Please wait before retrying.",
            status_code=429,
            errors=errors,
        )


class AuthenticationError(APIError):
    """Raised when authentication fails (HTTP 401 or 403)."""

    def __init__(self, errors: list[Any] | None = None) -> None:
        super().__init__(
            message="Authentication failed. Check your API token.",
            status_code=401,
            errors=errors,
        )


class NotFoundError(APIError):
    """Raised when the requested resource is not found (HTTP 404)."""

    def __init__(self, resource: str = "", errors: list[Any] | None = None) -> None:
        msg = f"Resource not found: '{resource}'" if resource else "Resource not found"
        super().__init__(message=msg, status_code=404, errors=errors)


class InvalidQueryError(OpenDOSMError):
    """Raised when query parameters are invalid before sending the request."""

    pass
