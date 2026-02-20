"""Wrapper for the OpenDOSM API (``/opendosm`` endpoint)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from opendosm.api.base import BaseAPI
from opendosm.http import HTTPClient
from opendosm.models import APIResponse
from opendosm.query import QueryBuilder


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
        query: Optional[QueryBuilder] = None,
        *,
        meta: bool = False,
        **extra_params: str,
    ) -> Union[List[Dict[str, Any]], APIResponse]:
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

    # ── Convenience helpers for popular datasets ───────────────────────

    def cpi(
        self,
        dataset_id: str = "cpi_core",
        query: Optional[QueryBuilder] = None,
        **kwargs: str,
    ) -> Union[List[Dict[str, Any]], APIResponse]:
        """Fetch Consumer Price Index data.

        Args:
            dataset_id: CPI dataset variant (default ``"cpi_core"``).
            query: Optional filters.
        """
        return self._get(dataset_id, query, **kwargs)

    def gdp(
        self,
        dataset_id: str = "gdp",
        query: Optional[QueryBuilder] = None,
        **kwargs: str,
    ) -> Union[List[Dict[str, Any]], APIResponse]:
        """Fetch Gross Domestic Product data.

        Args:
            dataset_id: GDP dataset variant (default ``"gdp"``).
            query: Optional filters.
        """
        return self._get(dataset_id, query, **kwargs)

    def population(
        self,
        dataset_id: str = "population_state",
        query: Optional[QueryBuilder] = None,
        **kwargs: str,
    ) -> Union[List[Dict[str, Any]], APIResponse]:
        """Fetch population data.

        Args:
            dataset_id: Population dataset variant (default ``"population_state"``).
            query: Optional filters.
        """
        return self._get(dataset_id, query, **kwargs)

    def trade(
        self,
        dataset_id: str = "trade",
        query: Optional[QueryBuilder] = None,
        **kwargs: str,
    ) -> Union[List[Dict[str, Any]], APIResponse]:
        """Fetch external trade data.

        Args:
            dataset_id: Trade dataset variant (default ``"trade"``).
            query: Optional filters.
        """
        return self._get(dataset_id, query, **kwargs)

    def labour(
        self,
        dataset_id: str = "lfs_month",
        query: Optional[QueryBuilder] = None,
        **kwargs: str,
    ) -> Union[List[Dict[str, Any]], APIResponse]:
        """Fetch labour force survey data.

        Args:
            dataset_id: Labour dataset variant (default ``"lfs_month"``).
            query: Optional filters.
        """
        return self._get(dataset_id, query, **kwargs)
