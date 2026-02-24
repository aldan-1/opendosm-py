"""Tests for the Pandas integration."""

import pytest

from opendosm.integrations.pandas import to_dataframe
from opendosm.models import APIResponse, DatasetInfo


class TestToDataframe:
    def test_from_list(self):
        pytest.importorskip("pandas")
        data = [
            {"date": "2023-01-01", "state": "Selangor", "value": 100},
            {"date": "2023-02-01", "state": "Johor", "value": 200},
        ]
        df = to_dataframe(data)
        assert len(df) == 2
        assert list(df.columns) == ["date", "state", "value"]

    def test_from_api_response(self):
        pytest.importorskip("pandas")
        resp = APIResponse(
            data=[
                {"date": "2023-01-01", "value": 42},
                {"date": "2023-02-01", "value": 43},
            ]
        )
        df = to_dataframe(resp)
        assert len(df) == 2

    def test_date_inference(self):
        pd = pytest.importorskip("pandas")
        data = [{"date": "2023-01-01", "value": 1}]
        df = to_dataframe(data)
        assert pd.api.types.is_datetime64_any_dtype(df["date"])

    def test_invalid_type_raises(self):
        pytest.importorskip("pandas")
        with pytest.raises(TypeError, match="Expected list or APIResponse"):
            to_dataframe("not valid")

    def test_empty_data(self):
        pytest.importorskip("pandas")
        df = to_dataframe([])
        assert len(df) == 0


class TestDatasetInfoConversion:
    """Tests for converting DatasetInfo Pydantic models to DataFrame."""

    def test_list_of_dataset_info(self):
        pd = pytest.importorskip("pandas")
        datasets = [
            DatasetInfo(
                id="fuelprice",
                title_en="Price of Petroleum & Diesel",
                category_en="Prices",
                source="KPDN, DOSM",
                frequency="WEEKLY",
            ),
            DatasetInfo(
                id="births",
                title_en="Daily Live Births",
                category_en="Demography",
                source="JPN",
                frequency="DAILY",
            ),
        ]
        df = to_dataframe(datasets)
        assert len(df) == 2
        assert "id" in df.columns
        assert "title_en" in df.columns
        assert df.iloc[0]["id"] == "fuelprice"
        assert df.iloc[1]["category_en"] == "Demography"

    def test_dataset_info_preserves_all_columns(self):
        pytest.importorskip("pandas")
        ds = DatasetInfo(
            id="test",
            title_en="Test Dataset",
            title_bm="Set Data Ujian",
            category_en="Cat",
            category_bm="Kat",
            subcategory_en="Sub",
            source="SRC",
            frequency="DAILY",
            geography="NATIONAL",
            dataset_begin="2020",
            dataset_end="2025",
        )
        df = to_dataframe([ds])
        # Should have all DatasetInfo fields as columns
        for field in ["id", "title_en", "title_bm", "category_en", "source",
                       "frequency", "geography", "dataset_begin", "dataset_end"]:
            assert field in df.columns


class TestNumericCoercion:
    """Tests for automatic numeric type coercion."""

    def test_none_in_numeric_column(self):
        pd = pytest.importorskip("pandas")
        data = [
            {"name": "a", "value": 2.05},
            {"name": "b", "value": None},
            {"name": "c", "value": 2.10},
        ]
        df = to_dataframe(data)
        assert pd.api.types.is_float_dtype(df["value"])

    def test_string_column_not_coerced(self):
        pd = pytest.importorskip("pandas")
        data = [
            {"name": "Selangor", "value": 100},
            {"name": "Johor", "value": 200},
        ]
        df = to_dataframe(data)
        # String column should stay as string/object
        assert not pd.api.types.is_numeric_dtype(df["name"])

    def test_mixed_none_numeric_string_stays_object(self):
        pd = pytest.importorskip("pandas")
        data = [
            {"col": "hello"},
            {"col": None},
            {"col": "world"},
        ]
        df = to_dataframe(data)
        # Mostly strings with None → should NOT become numeric
        assert not pd.api.types.is_numeric_dtype(df["col"])

    def test_all_none_column(self):
        pd = pytest.importorskip("pandas")
        data = [
            {"val": None},
            {"val": None},
        ]
        df = to_dataframe(data)
        # All-None should convert (NaN is numeric)
        assert len(df) == 2
