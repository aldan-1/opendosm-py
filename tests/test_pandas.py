"""Tests for the Pandas integration."""

import pytest

from opendosm.integrations.pandas import to_dataframe
from opendosm.models import APIResponse


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
