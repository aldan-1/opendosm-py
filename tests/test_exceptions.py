"""Tests for exception classes."""

from opendosm.exceptions import (
    APIError,
    AuthenticationError,
    InvalidQueryError,
    NotFoundError,
    OpenDOSMError,
    RateLimitError,
)


class TestExceptionHierarchy:
    def test_api_error_is_opendosm_error(self):
        assert issubclass(APIError, OpenDOSMError)

    def test_rate_limit_is_api_error(self):
        assert issubclass(RateLimitError, APIError)

    def test_auth_error_is_api_error(self):
        assert issubclass(AuthenticationError, APIError)

    def test_not_found_is_api_error(self):
        assert issubclass(NotFoundError, APIError)

    def test_invalid_query_is_opendosm_error(self):
        assert issubclass(InvalidQueryError, OpenDOSMError)

    def test_invalid_query_is_not_api_error(self):
        assert not issubclass(InvalidQueryError, APIError)


class TestAPIErrorFormatting:
    def test_str_with_errors(self):
        e = APIError("request failed", status_code=500, errors=["bad input", "timeout"])
        s = str(e)
        assert "[500]" in s
        assert "bad input" in s
        assert "timeout" in s

    def test_str_without_errors(self):
        e = APIError("request failed", status_code=500)
        s = str(e)
        assert "[500]" in s
        assert "request failed" in s


class TestRateLimitError:
    def test_retry_after_attribute(self):
        e = RateLimitError(retry_after=5.0)
        assert e.retry_after == 5.0
        assert e.status_code == 429

    def test_retry_after_none(self):
        e = RateLimitError()
        assert e.retry_after is None


class TestNotFoundError:
    def test_with_resource_name(self):
        e = NotFoundError(resource="fuelprice")
        assert "fuelprice" in str(e)
        assert e.status_code == 404

    def test_without_resource_name(self):
        e = NotFoundError()
        assert "not found" in str(e).lower()
