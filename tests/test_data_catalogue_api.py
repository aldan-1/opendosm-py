"""Tests for the Data Catalogue API wrapper."""

import pytest

from opendosm.api.data_catalogue import DataCatalogueAPI
from opendosm.http import HTTPClient
from opendosm.models import DatasetInfo


SAMPLE_DATASETS = [
    {
        "id": "fuelprice",
        "source": "KPDN, DOSM",
        "title_bm": "Harga Minyak",
        "title_en": "Price of Petroleum & Diesel",
        "frequency": "WEEKLY",
        "geography": "NATIONAL",
        "demography": "",
        "category_bm": "Harga",
        "category_en": "Prices",
        "dataset_end": "2025",
        "date_created": "2023-10-12",
        "dataset_begin": "2017",
        "subcategory_bm": "Harga Pengguna",
        "subcategory_en": "Consumer Prices",
    },
    {
        "id": "births",
        "source": "JPN",
        "title_bm": "Kelahiran Hidup Harian",
        "title_en": "Daily Live Births",
        "frequency": "DAILY",
        "geography": "NATIONAL",
        "demography": "",
        "category_bm": "Demografi",
        "category_en": "Demography",
        "dataset_end": "2023",
        "date_created": "2023-09-14",
        "dataset_begin": "1920",
        "subcategory_bm": "Kelahiran",
        "subcategory_en": "Births",
    },
    {
        "id": "gdp_qtr_real",
        "source": "DOSM",
        "title_bm": "KDNK Suku Tahun Sebenar",
        "title_en": "Quarterly Real GDP",
        "frequency": "QUARTERLY",
        "geography": "NATIONAL",
        "demography": "",
        "category_bm": "Akaun Nasional",
        "category_en": "National Accounts",
        "dataset_end": "2025",
        "date_created": "2024-01-15",
        "dataset_begin": "2015",
        "subcategory_bm": "KDNK",
        "subcategory_en": "GDP",
    },
]


@pytest.fixture
def api(httpx_mock):
    client = HTTPClient()
    api = DataCatalogueAPI(client)
    yield api
    client.close()


class TestGet:
    def test_get_returns_list(self, httpx_mock, api):
        httpx_mock.add_response(json=[{"date": "2023-01", "ron95": 2.05}])
        result = api.get("fuelprice")
        assert result == [{"date": "2023-01", "ron95": 2.05}]

        request = httpx_mock.get_request()
        assert "id=fuelprice" in str(request.url)

    def test_get_with_query_builder(self, httpx_mock, api):
        from opendosm.query import QueryBuilder

        httpx_mock.add_response(json=[])
        query = QueryBuilder().limit(5).sort("date", descending=True)
        api.get("births", query=query)

        request = httpx_mock.get_request()
        url_str = str(request.url)
        assert "id=births" in url_str
        assert "limit=5" in url_str


class TestListDatasets:
    def test_list_all(self, httpx_mock, api):
        httpx_mock.add_response(json=SAMPLE_DATASETS)
        result = api.list_datasets()

        assert len(result) == 3
        assert all(isinstance(d, DatasetInfo) for d in result)
        assert result[0].id == "fuelprice"
        assert result[1].id == "births"
        assert result[2].id == "gdp_qtr_real"

    def test_filter_by_category(self, httpx_mock, api):
        httpx_mock.add_response(json=SAMPLE_DATASETS)
        result = api.list_datasets(category="Demography")

        assert len(result) == 1
        assert result[0].id == "births"

    def test_filter_by_category_case_insensitive(self, httpx_mock, api):
        httpx_mock.add_response(json=SAMPLE_DATASETS)
        result = api.list_datasets(category="demography")

        assert len(result) == 1
        assert result[0].id == "births"

    def test_filter_by_source(self, httpx_mock, api):
        httpx_mock.add_response(json=SAMPLE_DATASETS)
        result = api.list_datasets(source="DOSM")

        assert len(result) == 2
        assert result[0].id == "fuelprice"  # source includes "DOSM"
        assert result[1].id == "gdp_qtr_real"

    def test_filter_by_category_and_source(self, httpx_mock, api):
        httpx_mock.add_response(json=SAMPLE_DATASETS)
        result = api.list_datasets(category="Prices", source="DOSM")

        assert len(result) == 1
        assert result[0].id == "fuelprice"

    def test_empty_result(self, httpx_mock, api):
        httpx_mock.add_response(json=SAMPLE_DATASETS)
        result = api.list_datasets(category="Nonexistent")

        assert result == []

    def test_dataset_info_fields(self, httpx_mock, api):
        httpx_mock.add_response(json=SAMPLE_DATASETS)
        result = api.list_datasets()

        ds = result[0]
        assert ds.id == "fuelprice"
        assert ds.title_en == "Price of Petroleum & Diesel"
        assert ds.category_en == "Prices"
        assert ds.source == "KPDN, DOSM"
        assert ds.frequency == "WEEKLY"
        assert ds.geography == "NATIONAL"
        assert ds.dataset_begin == "2017"


class TestSearch:
    def test_search_by_id(self, httpx_mock, api):
        httpx_mock.add_response(json=SAMPLE_DATASETS)
        result = api.search("fuel")

        assert len(result) == 1
        assert result[0].id == "fuelprice"

    def test_search_by_title(self, httpx_mock, api):
        httpx_mock.add_response(json=SAMPLE_DATASETS)
        result = api.search("Petroleum")

        assert len(result) == 1
        assert result[0].id == "fuelprice"

    def test_search_case_insensitive(self, httpx_mock, api):
        httpx_mock.add_response(json=SAMPLE_DATASETS)
        result = api.search("GDP")

        assert len(result) == 1
        assert result[0].id == "gdp_qtr_real"

    def test_search_multiple_results(self, httpx_mock, api):
        httpx_mock.add_response(json=SAMPLE_DATASETS)
        result = api.search("a")  # matches "fuelprice" (Petroleum) and others

        assert len(result) >= 1

    def test_search_no_results(self, httpx_mock, api):
        httpx_mock.add_response(json=SAMPLE_DATASETS)
        result = api.search("zzzznonexistent")

        assert result == []


class TestEdgeCases:
    def test_get_with_meta(self, httpx_mock, api):
        httpx_mock.add_response(json={"meta": {"total": 1}, "data": [{"ron95": 2.05}]})
        from opendosm.models import APIResponse

        result = api.get("fuelprice", meta=True)
        assert isinstance(result, APIResponse)
        assert len(result.data) == 1

    def test_list_datasets_non_list_response(self, httpx_mock, api):
        """If the API returns a dict instead of a list, return empty."""
        httpx_mock.add_response(json={"error": "unexpected"})
        result = api.list_datasets()
        assert result == []

