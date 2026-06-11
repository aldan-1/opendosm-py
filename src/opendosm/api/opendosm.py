"""Wrapper for the OpenDOSM API (``/opendosm`` endpoint)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from opendosm.api.base import BaseAPI

if TYPE_CHECKING:
    from collections.abc import Callable

    from opendosm.http import HTTPClient
    from opendosm.models import APIResponse
    from opendosm.query import QueryBuilder


# ── Registry of convenience dataset aliases ────────────────────────
# Each entry creates a method on OpenDOSMAPI with the given default ID.

_CONVENIENCE_DATASETS: dict[str, str] = {
    "cpi": "cpi_core",
    "gdp": "gdp_qtr_real",
    "population": "population_state",
    "trade": "trade_sitc_1d",
    "labour": "lfs_month",
}


def _make_convenience_method(default_id: str) -> Callable[..., Any]:
    """Build a convenience method that fetches *default_id* by default."""
    # Build a docstring once so it's attached to the generated method.
    _doc = (
        f"Fetch {default_id} data.\n\n"
        f"Args:\n"
        f"    dataset_id: Dataset identifier (default ``{default_id}``).\n"
        f"    query: Optional ``QueryBuilder`` with filters, sorting, limits.\n"
        f"    meta: If ``True``, returns an ``APIResponse`` with metadata.\n"
        f"    **extra_params: Additional raw query parameters.\n"
    )

    def method(
        self: OpenDOSMAPI,
        dataset_id: str = default_id,
        query: QueryBuilder | None = None,
        *,
        meta: bool = False,
        **extra_params: str,
    ) -> list[dict[str, Any]] | APIResponse:
        """Fetch data. See ``_CONVENIENCE_DATASETS`` for default IDs."""
        return self._get(dataset_id, query, meta=meta, **extra_params)

    method.__doc__ = _doc
    return method


# ── API class ──────────────────────────────────────────────────────


class OpenDOSMAPI(BaseAPI):
    """Access the OpenDOSM statistical data catalogue.

    This wraps the ``/opendosm`` endpoint, which provides datasets from the
    Department of Statistics Malaysia (DOSM) — population, CPI, GDP, trade, etc.

    Example::

        from opendosm import OpenDOSM

        client = OpenDOSM()
        records = client.opendosm.get("cpi_core", limit=10)
    """

    def __init__(self, http: HTTPClient) -> None:
        super().__init__(http, path="/opendosm")

    # ── Generic access ─────────────────────────────────────────────────

    def get(
        self,
        dataset_id: str,
        query: QueryBuilder | None = None,
        *,
        meta: bool = False,
        **extra_params: str,
    ) -> list[dict[str, Any]] | APIResponse:
        """Fetch any OpenDOSM dataset by its ID.

        Args:
            dataset_id: The dataset identifier, e.g. ``"cpi_core"``, ``"population_state"``.
                Find available IDs at https://open.dosm.gov.my/data-catalogue
            query: Optional ``QueryBuilder`` with filters, sorting, limits, etc.
            meta: If ``True``, returns an ``APIResponse`` with metadata.
            **extra_params: Additional raw query parameters.

        Returns:
            A list of record dicts, or ``APIResponse`` if ``meta=True``.
        """
        return self._get(dataset_id, query, meta=meta, **extra_params)


# Dynamically attach convenience methods from the registry.
for _name, _default_id in _CONVENIENCE_DATASETS.items():
    setattr(OpenDOSMAPI, _name, _make_convenience_method(_default_id))
