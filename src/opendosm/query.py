"""Fluent query builder for OpenDOSM API query parameters."""

from __future__ import annotations

from typing import TYPE_CHECKING

from opendosm.exceptions import InvalidQueryError

if TYPE_CHECKING:
    from collections.abc import Sequence


class QueryBuilder:
    """Builds URL query parameters for the data.gov.my API.

    Provides a fluent, chainable interface for constructing queries:

        >>> query = (QueryBuilder()
        ...     .filter(state="Selangor")
        ...     .sort("date", descending=True)
        ...     .limit(100)
        ...     .include("date", "state", "value"))
        >>> query.build()
        {'filter': 'Selangor@state', 'sort': '-date', 'limit': '100', 'include': 'date,state,value'}
    """

    def __init__(self) -> None:
        self._params: dict[str, str] = {}

    # ── Row-level filters ──────────────────────────────────────────────

    def filter(self, **kwargs: str) -> QueryBuilder:
        """Exact, case-sensitive filter.  ``?filter=<value>@<column>``"""
        parts = [f"{v}@{k}" for k, v in kwargs.items()]
        self._params["filter"] = ",".join(parts)
        return self

    def ifilter(self, **kwargs: str) -> QueryBuilder:
        """Exact, case-*insensitive* filter.  ``?ifilter=<value>@<column>``"""
        parts = [f"{v}@{k}" for k, v in kwargs.items()]
        self._params["ifilter"] = ",".join(parts)
        return self

    def contains(self, **kwargs: str) -> QueryBuilder:
        """Partial, case-sensitive match.  ``?contains=<value>@<column>``"""
        parts = [f"{v}@{k}" for k, v in kwargs.items()]
        self._params["contains"] = ",".join(parts)
        return self

    def icontains(self, **kwargs: str) -> QueryBuilder:
        """Partial, case-*insensitive* match.  ``?icontains=<value>@<column>``"""
        parts = [f"{v}@{k}" for k, v in kwargs.items()]
        self._params["icontains"] = ",".join(parts)
        return self

    def range(self, column: str, begin: int | float | None = None,
              end: int | float | None = None) -> QueryBuilder:
        """Numerical range filter.  ``?range=<column>[<begin>:<end>]``"""
        begin_str = str(begin) if begin is not None else ""
        end_str = str(end) if end is not None else ""
        self._params["range"] = f"{column}[{begin_str}:{end_str}]"
        return self

    # ── Sorting ────────────────────────────────────────────────────────

    def sort(self, *columns: str, descending: bool | Sequence[bool] = False) -> QueryBuilder:
        """Sort by one or more columns.

        Args:
            columns: Column names to sort by.
            descending: If a single bool, applies to all columns.
                If a sequence of bools, must match the number of columns.
        """
        if isinstance(descending, bool):
            flags = [descending] * len(columns)
        else:
            flags = list(descending)
            if len(flags) != len(columns):
                raise InvalidQueryError(
                    f"descending has {len(flags)} values but {len(columns)} columns given"
                )

        parts: list[str] = []
        for col, desc in zip(columns, flags):  # noqa: B905 — lengths validated above
            parts.append(f"-{col}" if desc else col)
        self._params["sort"] = ",".join(parts)
        return self

    # ── Date / timestamp range ─────────────────────────────────────────

    def date_range(
        self,
        column: str,
        start: str | None = None,
        end: str | None = None,
    ) -> QueryBuilder:
        """Filter by date range (``YYYY-MM-DD``).

        Args:
            column: The date column name.
            start: Start date inclusive (``YYYY-MM-DD``).
            end: End date inclusive (``YYYY-MM-DD``).
        """
        if start:
            self._params["date_start"] = f"{start}@{column}"
        if end:
            self._params["date_end"] = f"{end}@{column}"
        return self

    def timestamp_range(
        self,
        column: str,
        start: str | None = None,
        end: str | None = None,
    ) -> QueryBuilder:
        """Filter by timestamp range (``YYYY-MM-DD HH:MM:SS``).

        Args:
            column: The timestamp column name.
            start: Start timestamp inclusive.
            end: End timestamp inclusive.
        """
        if start:
            self._params["timestamp_start"] = f"{start}@{column}"
        if end:
            self._params["timestamp_end"] = f"{end}@{column}"
        return self

    # ── Pagination ─────────────────────────────────────────────────────

    def limit(self, n: int) -> QueryBuilder:
        """Limit the number of records returned."""
        if n < 0:
            raise InvalidQueryError("limit must be a non-negative integer")
        self._params["limit"] = str(n)
        return self

    # ── Column selection ───────────────────────────────────────────────

    def include(self, *columns: str) -> QueryBuilder:
        """Include only the specified columns in the response."""
        self._params["include"] = ",".join(columns)
        return self

    def exclude(self, *columns: str) -> QueryBuilder:
        """Exclude the specified columns from the response."""
        self._params["exclude"] = ",".join(columns)
        return self

    # ── Meta ───────────────────────────────────────────────────────────

    def with_meta(self, enabled: bool = True) -> QueryBuilder:
        """Request metadata alongside data (``?meta=true``)."""
        if enabled:
            self._params["meta"] = "true"
        else:
            self._params.pop("meta", None)
        return self

    # ── Build ──────────────────────────────────────────────────────────

    def build(self) -> dict[str, str]:
        """Return the accumulated query parameters as a dict."""
        return dict(self._params)

    def __repr__(self) -> str:
        return f"QueryBuilder({self._params!r})"
