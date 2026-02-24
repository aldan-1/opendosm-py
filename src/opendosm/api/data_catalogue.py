"""Wrapper for the Data Catalogue API (``/data-catalogue`` endpoint)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from opendosm.api.base import BaseAPI
from opendosm.models import DatasetInfo

if TYPE_CHECKING:
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
        records = client.data_catalogue.get("fuelprice", limit=5)

        # Discover available datasets
        datasets = client.data_catalogue.list_datasets()
        gdp_datasets = client.data_catalogue.search("gdp")
    """

    def __init__(self, http: HTTPClient) -> None:
        super().__init__(http, path="/data-catalogue")

    def get(
        self,
        dataset_id: str,
        query: QueryBuilder | None = None,
        *,
        meta: bool = False,
        **extra_params: str,
    ) -> list[dict[str, Any]] | APIResponse:
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

    # ── Dataset discovery ──────────────────────────────────────────────

    def list_datasets(
        self,
        *,
        category: str | None = None,
        source: str | None = None,
    ) -> list[DatasetInfo]:
        """List all available datasets in the Data Catalogue.

        Fetches the ``datasets`` meta-dataset from the API and returns
        structured ``DatasetInfo`` objects.  Results are always live from
        the API, so new datasets added by DOSM appear automatically.

        Args:
            category: Optional filter by ``category_en`` (case-insensitive).
                Example: ``"Demography"``, ``"National Accounts"``.
            source: Optional filter by data source (case-insensitive).
                Example: ``"DOSM"``, ``"BNM"``.

        Returns:
            A list of ``DatasetInfo`` objects.

        Example::

            client = OpenDOSM()

            # All datasets
            all_ds = client.data_catalogue.list_datasets()

            # Filter by category
            demo = client.data_catalogue.list_datasets(category="Demography")
        """
        raw = self._get("datasets")
        if not isinstance(raw, list):
            return []

        datasets = [DatasetInfo.model_validate(record) for record in raw]

        if category is not None:
            cat_lower = category.lower()
            datasets = [d for d in datasets if d.category_en.lower() == cat_lower]

        if source is not None:
            src_lower = source.lower()
            datasets = [d for d in datasets if src_lower in d.source.lower()]

        return datasets

    def search(self, query: str) -> list[DatasetInfo]:
        """Search for datasets by keyword.

        Performs a case-insensitive search across dataset ``id`` and
        ``title_en`` fields.

        Args:
            query: The search term (e.g. ``"gdp"``, ``"fuel"``, ``"population"``).

        Returns:
            A list of matching ``DatasetInfo`` objects.

        Example::

            client = OpenDOSM()
            results = client.data_catalogue.search("trade")
            for ds in results:
                print(f"{ds.id}: {ds.title_en}")
        """
        q = query.lower()
        all_datasets = self.list_datasets()
        return [
            d for d in all_datasets
            if q in d.id.lower() or q in d.title_en.lower()
        ]
