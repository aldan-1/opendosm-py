"""Tests for the QueryBuilder."""

import pytest

from opendosm.exceptions import InvalidQueryError
from opendosm.query import QueryBuilder


class TestFilter:
    def test_single_filter(self):
        q = QueryBuilder().filter(state="Selangor")
        assert q.build() == {"filter": "Selangor@state"}

    def test_multiple_filters(self):
        q = QueryBuilder().filter(state="Selangor", year="2023")
        params = q.build()
        assert "filter" in params
        # Order of kwargs may vary, so check both parts exist
        assert "Selangor@state" in params["filter"]
        assert "2023@year" in params["filter"]

    def test_ifilter(self):
        q = QueryBuilder().ifilter(state="selangor")
        assert q.build() == {"ifilter": "selangor@state"}


class TestContains:
    def test_contains(self):
        q = QueryBuilder().contains(name="Kuala")
        assert q.build() == {"contains": "Kuala@name"}

    def test_icontains(self):
        q = QueryBuilder().icontains(name="kuala")
        assert q.build() == {"icontains": "kuala@name"}


class TestRange:
    def test_full_range(self):
        q = QueryBuilder().range("value", begin=10, end=100)
        assert q.build() == {"range": "value[10:100]"}

    def test_open_start(self):
        q = QueryBuilder().range("value", end=50)
        assert q.build() == {"range": "value[:50]"}

    def test_open_end(self):
        q = QueryBuilder().range("value", begin=10)
        assert q.build() == {"range": "value[10:]"}


class TestSort:
    def test_ascending(self):
        q = QueryBuilder().sort("date")
        assert q.build() == {"sort": "date"}

    def test_descending(self):
        q = QueryBuilder().sort("date", descending=True)
        assert q.build() == {"sort": "-date"}

    def test_multiple_mixed(self):
        q = QueryBuilder().sort("state", "date", descending=[False, True])
        assert q.build() == {"sort": "state,-date"}

    def test_mismatched_descending_raises(self):
        with pytest.raises(InvalidQueryError, match="values"):
            QueryBuilder().sort("a", "b", descending=[True])


class TestDateRange:
    def test_date_range_both(self):
        q = QueryBuilder().date_range("date", start="2023-01-01", end="2023-12-31")
        params = q.build()
        assert params["date_start"] == "2023-01-01@date"
        assert params["date_end"] == "2023-12-31@date"

    def test_date_range_start_only(self):
        q = QueryBuilder().date_range("date", start="2023-01-01")
        params = q.build()
        assert params["date_start"] == "2023-01-01@date"
        assert "date_end" not in params


class TestTimestamp:
    def test_timestamp_range(self):
        q = QueryBuilder().timestamp_range(
            "created_at",
            start="2023-01-01 00:00:00",
            end="2023-12-31 23:59:59",
        )
        params = q.build()
        assert params["timestamp_start"] == "2023-01-01 00:00:00@created_at"
        assert params["timestamp_end"] == "2023-12-31 23:59:59@created_at"


class TestLimit:
    def test_limit(self):
        q = QueryBuilder().limit(10)
        assert q.build() == {"limit": "10"}

    def test_negative_limit_raises(self):
        with pytest.raises(InvalidQueryError, match="non-negative"):
            QueryBuilder().limit(-1)


class TestColumnSelection:
    def test_include(self):
        q = QueryBuilder().include("date", "state", "value")
        assert q.build() == {"include": "date,state,value"}

    def test_exclude(self):
        q = QueryBuilder().exclude("id")
        assert q.build() == {"exclude": "id"}


class TestMeta:
    def test_with_meta(self):
        q = QueryBuilder().with_meta()
        assert q.build() == {"meta": "true"}

    def test_with_meta_false(self):
        q = QueryBuilder().with_meta(True).with_meta(False)
        assert "meta" not in q.build()


class TestEdgeCases:
    def test_empty_build(self):
        q = QueryBuilder()
        assert q.build() == {}

    def test_date_range_end_only(self):
        q = QueryBuilder().date_range("date", end="2023-12-31")
        params = q.build()
        assert "date_start" not in params
        assert params["date_end"] == "2023-12-31@date"

    def test_include_and_exclude_together(self):
        q = QueryBuilder().include("date", "value").exclude("id")
        params = q.build()
        assert "include" in params
        assert "exclude" in params

    def test_limit_zero(self):
        q = QueryBuilder().limit(0)
        assert q.build() == {"limit": "0"}

    def test_repr(self):
        q = QueryBuilder().limit(5)
        assert "limit" in repr(q)


class TestChaining:
    def test_fluent_chaining(self):
        q = (
            QueryBuilder()
            .filter(state="Selangor")
            .sort("date", descending=True)
            .limit(50)
            .include("date", "value")
        )
        params = q.build()
        assert params["filter"] == "Selangor@state"
        assert params["sort"] == "-date"
        assert params["limit"] == "50"
        assert params["include"] == "date,value"
