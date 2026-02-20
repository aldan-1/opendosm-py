"""Wrapper for the Data Catalogue API (``/data-catalogue`` endpoint)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from opendosm.api.base import BaseAPI
from opendosm.http import HTTPClient
from opendosm.models import APIResponse
from opendosm.query import QueryBuilder


class DataCatalogueAPI(BaseAPI):
    """Access the general data.gov.my Data Catalogue.

    This wraps the ``/data-catalogue`` endpoint, which provides access to
    a broader set of government datasets beyond DOSM statistics.

    Example::

        from opendosm import OpenDOSM

        client = OpenDOSM()
        records = client.data_catalogue.get("some_dataset_id", limit=20)
    """

    def __init__(self, http: HTTPClient) -> None:
        super().__init__(http, path="/data-catalogue")

    def get(
        self,
        dataset_id: str,
        query: Optional[QueryBuilder] = None,
        *,
        meta: bool = False,
        **extra_params: str,
    ) -> Union[List[Dict[str, Any]], APIResponse]:
        """Fetch any Data Catalogue dataset by its ID.

        Args:
            dataset_id: The dataset identifier.
            query: Optional ``QueryBuilder`` with filters, sorting, limits, etc.
            meta: If ``True``, returns an ``APIResponse`` with metadata.
            **extra_params: Additional raw query parameters.

        Returns:
            A list of record dicts, or ``APIResponse`` if ``meta=True``.
        """
        return self._get(dataset_id, query, meta=meta, **extra_params)
