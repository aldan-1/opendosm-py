"""Tests for the OpenDOSM API wrapper."""

import pytest

from opendosm.api.opendosm import OpenDOSMAPI
from opendosm.http import HTTPClient
from opendosm.models import APIResponse
from opendosm.query import QueryBuilder


@pytest.fixture
def api(httpx_mock):
    client = HTTPClient()
    api = OpenDOSMAPI(client)
    yield api
    client.close()


class TestGet:
    def test_get_returns_list(self, httpx_mock, api):
        httpx_mock.add_response(json=[{"date": "2023-01", "value": 100}])
        result = api.get("cpi_core")
        assert result == [{"date": "2023-01", "value": 100}]

        request = httpx_mock.get_request()
        assert "id=cpi_core" in str(request.url)

    def test_get_with_meta(self, httpx_mock, api):
        httpx_mock.add_response(json={"meta": {}, "data": [{"a": 1}]})
        result = api.get("cpi_core", meta=True)
        assert isinstance(result, APIResponse)
        assert len(result.data) == 1

    def test_get_with_query_builder(self, httpx_mock, api):
        httpx_mock.add_response(json=[])
        query = QueryBuilder().filter(state="Selangor").limit(10)
        api.get("population_state", query=query)

        request = httpx_mock.get_request()
        url_str = str(request.url)
        assert "id=population_state" in url_str
        assert "filter=Selangor%40state" in url_str or "filter=Selangor@state" in url_str
        assert "limit=10" in url_str


class TestConvenienceMethods:
    def test_cpi(self, httpx_mock, api):
        httpx_mock.add_response(json=[{"value": 100}])
        api.cpi()
        request = httpx_mock.get_request()
        assert "id=cpi_core" in str(request.url)

    def test_gdp(self, httpx_mock, api):
        httpx_mock.add_response(json=[{"value": 200}])
        api.gdp()
        request = httpx_mock.get_request()
        assert "id=gdp_qtr_real" in str(request.url)

    def test_population(self, httpx_mock, api):
        httpx_mock.add_response(json=[{"value": 300}])
        api.population()
        request = httpx_mock.get_request()
        assert "id=population_state" in str(request.url)

    def test_trade(self, httpx_mock, api):
        httpx_mock.add_response(json=[{"value": 400}])
        api.trade()
        request = httpx_mock.get_request()
        assert "id=trade_sitc_1d" in str(request.url)

    def test_labour(self, httpx_mock, api):
        httpx_mock.add_response(json=[{"value": 500}])
        api.labour()
        request = httpx_mock.get_request()
        assert "id=lfs_month" in str(request.url)

    def test_convenience_with_custom_id(self, httpx_mock, api):
        httpx_mock.add_response(json=[{"value": 1}])
        api.gdp(dataset_id="gdp_annual")
        request = httpx_mock.get_request()
        assert "id=gdp_annual" in str(request.url)


class TestMetaAndQuery:
    def test_meta_and_query_combined(self, httpx_mock, api):
        httpx_mock.add_response(json={"meta": {"total": 1}, "data": [{"v": 1}]})
        query = QueryBuilder().limit(5)
        result = api.get("cpi_core", query=query, meta=True)
        assert isinstance(result, APIResponse)

        request = httpx_mock.get_request()
        url_str = str(request.url)
        assert "limit=5" in url_str
        assert "meta=true" in url_str

