"""OpenDOSM — A Pythonic SDK for Malaysia's Open Data API.

Quick start::

    from opendosm import OpenDOSM

    client = OpenDOSM()
    data = client.opendosm.get("cpi_core", limit=10)
    print(data)
"""

from __future__ import annotations

from opendosm._version import __version__
from opendosm.client import OpenDOSM
from opendosm.exceptions import (
    APIError,
    AuthenticationError,
    InvalidQueryError,
    NotFoundError,
    OpenDOSMError,
    RateLimitError,
)
from opendosm.models import APIResponse, DatasetInfo, MetaInfo
from opendosm.query import QueryBuilder

__all__ = [
    "OpenDOSM",
    "QueryBuilder",
    "APIResponse",
    "DatasetInfo",
    "MetaInfo",
    "OpenDOSMError",
    "APIError",
    "RateLimitError",
    "AuthenticationError",
    "NotFoundError",
    "InvalidQueryError",
    "__version__",
]
