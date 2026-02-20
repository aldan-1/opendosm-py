"""Low-level HTTP transport for the OpenDOSM SDK."""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from opendosm.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
)

logger = logging.getLogger("opendosm")

_DEFAULT_BASE_URL = "https://api.data.gov.my"
_DEFAULT_TIMEOUT = 30.0
_MAX_RETRIES = 3
_INITIAL_BACKOFF = 1.0  # seconds


class HTTPClient:
    """Thin wrapper around ``httpx.Client`` that handles auth, retries, and errors.

    Args:
        base_url: Base URL for all requests.
        token: Optional API token for higher rate limits.
        timeout: Request timeout in seconds.
        max_retries: Maximum number of retries on 429 rate-limit responses.
    """

    def __init__(
        self,
        base_url: str = _DEFAULT_BASE_URL,
        token: str | None = None,
        timeout: float = _DEFAULT_TIMEOUT,
        max_retries: int = _MAX_RETRIES,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries

        headers: dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": "opendosm-py/0.1.0",
        }
        if token:
            headers["Authorization"] = f"Token {token}"

        self._client = httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
        )

    # ── Public API ─────────────────────────────────────────────────────

    def get(self, path: str, params: dict[str, str] | None = None) -> Any:
        """Send a GET request and return the parsed JSON response.

        Automatically retries on HTTP 429 with exponential backoff.

        Args:
            path: URL path relative to the base URL (e.g. ``/opendosm``).
            params: URL query parameters.

        Returns:
            Parsed JSON response (list or dict).

        Raises:
            RateLimitError: If rate limit is still exceeded after all retries.
            AuthenticationError: On 401/403 responses.
            NotFoundError: On 404 responses.
            APIError: On any other non-200 response.
        """
        backoff = _INITIAL_BACKOFF

        for attempt in range(self.max_retries + 1):
            logger.debug("GET %s params=%s (attempt %d)", path, params, attempt + 1)
            response = self._client.get(path, params=params)

            if response.status_code == 200:
                return response.json()

            if response.status_code == 429:
                retry_after = self._parse_retry_after(response)
                if attempt < self.max_retries:
                    wait = retry_after if retry_after else backoff
                    logger.warning("Rate limited. Retrying in %.1fs …", wait)
                    time.sleep(wait)
                    backoff *= 2
                    continue
                raise RateLimitError(retry_after=retry_after)

            # Non-retryable errors
            self._raise_for_status(response)

        # Should not reach here, but just in case
        raise APIError("Unexpected error after retries", status_code=0)  # pragma: no cover

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    # ── Internals ──────────────────────────────────────────────────────

    @staticmethod
    def _parse_retry_after(response: httpx.Response) -> float | None:
        raw = response.headers.get("Retry-After")
        if raw is not None:
            try:
                return float(raw)
            except ValueError:
                return None
        return None

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        """Raise a specific exception based on the HTTP status code."""
        errors = []
        try:
            body = response.json()
            if isinstance(body, dict):
                errors = body.get("errors", [])
        except Exception:
            pass

        status = response.status_code

        if status in (401, 403):
            raise AuthenticationError(errors=errors)
        if status == 404:
            raise NotFoundError(errors=errors)

        raise APIError(
            message=f"API request failed with status {status}",
            status_code=status,
            errors=errors,
        )

    # ── Context manager ────────────────────────────────────────────────

    def __enter__(self) -> HTTPClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
