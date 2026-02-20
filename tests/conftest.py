"""Shared pytest fixtures for the OpenDOSM SDK test suite."""

import pytest

from opendosm.http import HTTPClient


@pytest.fixture
def mock_client(httpx_mock):
    """Provide an HTTPClient instance with a mocked transport."""
    client = HTTPClient(base_url="https://api.data.gov.my")
    yield client
    client.close()
