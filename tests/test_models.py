"""Tests for Pydantic response models."""

from opendosm.models import APIResponse, ErrorResponse


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


class TestErrorResponse:
    def test_parse_error(self):
        raw = {"status": 400, "errors": ["Invalid parameter"]}
        err = ErrorResponse.model_validate(raw)
        assert err.status == 400
        assert len(err.errors) == 1
