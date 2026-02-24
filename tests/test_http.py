"""Tests for the HTTP client layer."""

import pytest

from opendosm.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
)
from opendosm.http import HTTPClient


class TestSuccessfulRequests:
    def test_get_returns_json_list(self, httpx_mock, mock_client):
        httpx_mock.add_response(json=[{"date": "2023-01", "value": 100}])
        result = mock_client.get("/opendosm", params={"id": "cpi_core"})
        assert result == [{"date": "2023-01", "value": 100}]

    def test_get_returns_json_dict(self, httpx_mock, mock_client):
        httpx_mock.add_response(json={"meta": {}, "data": [{"a": 1}]})
        result = mock_client.get("/opendosm", params={"id": "cpi_core", "meta": "true"})
        assert result == {"meta": {}, "data": [{"a": 1}]}


class TestAuthentication:
    def test_token_sent_in_header(self, httpx_mock):
        httpx_mock.add_response(json=[])
        client = HTTPClient(token="my-secret-token")
        client.get("/opendosm", params={"id": "test"})
        client.close()

        request = httpx_mock.get_request()
        assert request.headers["Authorization"] == "Token my-secret-token"

    def test_no_token_no_header(self, httpx_mock):
        httpx_mock.add_response(json=[])
        client = HTTPClient()
        client.get("/opendosm", params={"id": "test"})
        client.close()

        request = httpx_mock.get_request()
        assert "Authorization" not in request.headers


class TestErrorHandling:
    def test_401_raises_authentication_error(self, httpx_mock, mock_client):
        httpx_mock.add_response(status_code=401, json={"status": 401, "errors": ["Invalid token"]})
        with pytest.raises(AuthenticationError):
            mock_client.get("/opendosm")

    def test_403_raises_authentication_error(self, httpx_mock, mock_client):
        httpx_mock.add_response(status_code=403, json={"status": 403, "errors": []})
        with pytest.raises(AuthenticationError):
            mock_client.get("/opendosm")

    def test_404_raises_not_found_error(self, httpx_mock, mock_client):
        httpx_mock.add_response(status_code=404, json={"status": 404, "errors": ["Not found"]})
        with pytest.raises(NotFoundError):
            mock_client.get("/opendosm")

    def test_500_raises_api_error(self, httpx_mock, mock_client):
        httpx_mock.add_response(status_code=500, json={"status": 500, "errors": ["Server error"]})
        with pytest.raises(APIError) as exc_info:
            mock_client.get("/opendosm")
        assert exc_info.value.status_code == 500


class TestRateLimiting:
    def test_429_retries_then_succeeds(self, httpx_mock, mock_client):
        # First call: 429, second call: 200
        httpx_mock.add_response(status_code=429, json={"status": 429, "errors": []})
        httpx_mock.add_response(json=[{"value": 42}])

        # Override backoff for fast tests
        result = mock_client.get("/opendosm", params={"id": "test"})
        assert result == [{"value": 42}]

    def test_429_exhausted_raises_rate_limit_error(self, httpx_mock):
        client = HTTPClient(max_retries=1)
        httpx_mock.add_response(status_code=429, json={"status": 429, "errors": []})
        httpx_mock.add_response(status_code=429, json={"status": 429, "errors": []})

        with pytest.raises(RateLimitError):
            client.get("/opendosm")
        client.close()


class TestRetryAfterHeader:
    def test_retry_after_header_respected(self, httpx_mock):
        """429 with Retry-After header should use that value."""
        httpx_mock.add_response(
            status_code=429,
            headers={"Retry-After": "0.01"},
            json={"status": 429, "errors": []},
        )
        httpx_mock.add_response(json=[{"value": 1}])

        client = HTTPClient(max_retries=1)
        result = client.get("/opendosm")
        assert result == [{"value": 1}]
        client.close()

    def test_invalid_retry_after_falls_back(self, httpx_mock):
        """Invalid Retry-After header falls back to exponential backoff."""
        httpx_mock.add_response(
            status_code=429,
            headers={"Retry-After": "not-a-number"},
            json={"status": 429, "errors": []},
        )
        httpx_mock.add_response(json=[{"value": 2}])

        client = HTTPClient(max_retries=1)
        result = client.get("/opendosm")
        assert result == [{"value": 2}]
        client.close()


class TestNonJsonError:
    def test_non_json_error_body(self, httpx_mock):
        """HTML error body should not crash the error parser."""
        httpx_mock.add_response(
            status_code=502,
            text="<html><body>Bad Gateway</body></html>",
            headers={"Content-Type": "text/html"},
        )
        with pytest.raises(APIError) as exc_info:
            client = HTTPClient()
            try:
                client.get("/opendosm")
            finally:
                client.close()
        assert exc_info.value.status_code == 502


class TestContextManager:
    def test_context_manager(self, httpx_mock):
        httpx_mock.add_response(json=[])
        with HTTPClient() as client:
            result = client.get("/opendosm", params={"id": "test"})
        assert result == []
