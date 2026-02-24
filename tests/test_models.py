"""Tests for Pydantic response models."""

from opendosm.models import APIResponse, DatasetInfo, ErrorResponse, MetaInfo


class TestAPIResponse:
    def test_parse_meta_response(self):
        raw = {"meta": {"total": 100}, "data": [{"a": 1}, {"a": 2}]}
        resp = APIResponse.model_validate(raw)
        assert len(resp.data) == 2
        assert resp.meta is not None

    def test_parse_data_only(self):
        resp = APIResponse(data=[{"x": 1}])
        assert resp.meta is None
        assert len(resp.data) == 1


class TestDatasetInfo:
    def test_minimal_only_id(self):
        ds = DatasetInfo(id="test")
        assert ds.id == "test"
        assert ds.title_en == ""
        assert ds.source == ""

    def test_extra_fields_accepted(self):
        ds = DatasetInfo(id="test", future_field="new_value")
        assert ds.id == "test"
        assert ds.future_field == "new_value"


class TestAPIResponseDefaults:
    def test_empty_data(self):
        resp = APIResponse(data=[])
        assert resp.data == []
        assert resp.meta is None


class TestMetaInfo:
    def test_extra_fields_accepted(self):
        info = MetaInfo(total=100, custom_key="hello")
        assert info.total == 100
        assert info.custom_key == "hello"


class TestErrorResponse:
    def test_parse_error(self):
        raw = {"status": 400, "errors": ["Invalid parameter"]}
        err = ErrorResponse.model_validate(raw)
        assert err.status == 400
        assert len(err.errors) == 1
