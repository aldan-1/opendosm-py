"""Main OpenDOSM SDK client."""

from __future__ import annotations

from opendosm.api.data_catalogue import DataCatalogueAPI
from opendosm.api.opendosm import OpenDOSMAPI
from opendosm.http import HTTPClient


class OpenDOSM:
    """The main entry point for the OpenDOSM Python SDK.

    Provides access to both the OpenDOSM API (DOSM statistical data) and
    the general Data Catalogue API on data.gov.my.

    Args:
        token: Optional API token for increased rate limits.
            Request one at dataterbuka@jdn.gov.my
        base_url: Override the default API base URL.
        timeout: Request timeout in seconds (default 30).

    Example::

        from opendosm import OpenDOSM
        from opendosm.query import QueryBuilder

        client = OpenDOSM()

        # Fetch CPI data
        cpi_data = client.opendosm.cpi()

        # Fetch with filters
        query = QueryBuilder().filter(state="Selangor").limit(50)
        population = client.opendosm.population(query=query)

        # Convert to Pandas DataFrame
        df = client.to_dataframe(population)

        # Don't forget to close when done (or use as context manager)
        client.close()

    Context manager usage::

        with OpenDOSM(token="your-token") as client:
            data = client.opendosm.get("cpi_core", limit=10)
    """

    def __init__(
        self,
        token: str | None = None,
        base_url: str = "https://api.data.gov.my",
        timeout: float = 30.0,
    ) -> None:
        self._http = HTTPClient(base_url=base_url, token=token, timeout=timeout)

        # Sub-clients for each API family
        self.opendosm = OpenDOSMAPI(self._http)
        self.data_catalogue = DataCatalogueAPI(self._http)

    def to_dataframe(self, data: object) -> object:
        """Convert API response data to a Pandas DataFrame.

        Requires the ``pandas`` optional dependency::

            pip install opendosm[pandas]

        Args:
            data: A list of record dicts from the API, or an ``APIResponse`` object.

        Returns:
            A ``pandas.DataFrame``.

        Raises:
            ImportError: If pandas is not installed.
        """
        from opendosm.integrations.pandas import to_dataframe

        return to_dataframe(data)

    def close(self) -> None:
        """Close the underlying HTTP client and release resources."""
        self._http.close()

    def __enter__(self) -> OpenDOSM:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"OpenDOSM(base_url={self._http.base_url!r})"
