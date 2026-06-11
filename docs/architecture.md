# Architecture — opendosm-py

## Overview

A layered Python SDK for Malaysia's [data.gov.my Open API](https://developer.data.gov.my/), providing typed access to OpenDOSM statistical datasets and the Data Catalogue, with optional Pandas integration.

**License:** MIT | **Python:** ≥ 3.10 | **Runtime deps:** `httpx`, `pydantic`

---

## Module Structure

```
src/opendosm/
├── __init__.py          # Public exports, __version__
├── client.py            # OpenDOSM main client class (facade pattern)
├── http.py              # HTTPClient — httpx wrapper, retry, auth, error mapping
├── query.py             # QueryBuilder — fluent chainable API for query params
├── models.py            # Pydantic v2 models (APIResponse, DatasetInfo, etc.)
├── exceptions.py        # Exception hierarchy
├── py.typed             # PEP 561 type marker
├── api/
│   ├── base.py          # BaseAPI — shared _get() logic (template method)
│   ├── opendosm.py      # OpenDOSMAPI — /opendosm endpoint convenience methods
│   └── data_catalogue.py # DataCatalogueAPI — /data-catalogue + dataset discovery
└── integrations/
    └── pandas.py        # to_dataframe() with date parsing + numeric coercion
```

---

## Data Flow

```
User code → OpenDOSM client
  → OpenDOSMAPI / DataCatalogueAPI
    → QueryBuilder.build() → dict of params
    → HTTPClient.get(path, params)
      → httpx.Client (retries on 429, raises typed exceptions)
    → Returns list[dict] or APIResponse (if meta=True)
  → Optional: to_dataframe() → pandas DataFrame
```

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| `httpx` over `requests` | Native async support for future, modern API |
| Pydantic v2 with `extra="allow"` | Forward-compatible — API can add fields without breaking models |
| `QueryBuilder` as separate class | Reusable across all API wrappers, not tied to one endpoint |
| `list_datasets()` fetches `?id=datasets` | Dynamic discovery — always reflects latest catalogue |
| `to_dataframe()` on client, not response | Keeps pandas optional — import only when called |
| `from __future__ import annotations` | Forward reference support on Python 3.10+ |
| `py.typed` marker | Signals to mypy/pyright that the package has inline types |

---

## Exception Hierarchy

```
OpenDOSMError (base)
 └── APIError (status_code, errors)
      ├── RateLimitError (retry_after)
      ├── AuthenticationError
      ├── NotFoundError
 └── InvalidQueryError (client-side, before HTTP request)
```

---

## Rate Limits

Per the [official docs](https://developer.data.gov.my/rate-limit), all API endpoints are throttled at **4 requests per minute** regardless of authentication. The SDK retries on 429 with exponential backoff (3 retries, starting at 1s).

---

## Known Gotchas

- Dataset `iowrt_3d` listed in catalogue returns `NotFoundError` — handled gracefully
- CI badge URL needs `?branch=master` to show correct status in README
- `Retry-After` header parsing falls back to exponential backoff on invalid values
- Ruff rule `B905` is suppressed on one `zip()` call in `query.py:84` via `# noqa` (lengths validated above)
