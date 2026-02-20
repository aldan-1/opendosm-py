"""Base class for all API modules."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from opendosm.models import APIResponse

if TYPE_CHECKING:
    from opendosm.http import HTTPClient
    from opendosm.query import QueryBuilder


class BaseAPI:
    """Shared logic for API endpoint wrappers.

    Args:
        http: The shared HTTP client instance.
        path: The URL path prefix for this API (e.g. ``/opendosm``).
    """

    def __init__(self, http: HTTPClient, path: str) -> None:
        self._http = http
        self._path = path

    def _get(
        self,
        dataset_id: str,
        query: QueryBuilder | None = None,
        *,
        meta: bool = False,
        **extra_params: str,
    ) -> list[dict[str, Any]] | APIResponse:
        """Fetch data for a given dataset.

        Args:
            dataset_id: The dataset identifier (e.g. ``"cpi_core"``).
            query: Optional ``QueryBuilder`` instance with filters/sort/limit.
            meta: If ``True``, returns an ``APIResponse`` with metadata.
            **extra_params: Additional raw query parameters.

        Returns:
            A list of record dicts (default), or an ``APIResponse`` if ``meta=True``.
        """
        params: dict[str, str] = {"id": dataset_id}

        if query is not None:
            params.update(query.build())

        if meta:
            params["meta"] = "true"

        params.update(extra_params)

        raw = self._http.get(self._path, params=params)

        if meta and isinstance(raw, dict):
            return APIResponse.model_validate(raw)

        return cast("list[dict[str, Any]]", raw)
