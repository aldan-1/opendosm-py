# OpenDOSM Python SDK — User Guide (v0.1)

A comprehensive guide to using the `opendosm` Python SDK for accessing Malaysia's official open data from [data.gov.my](https://data.gov.my) and [OpenDOSM](https://open.dosm.gov.my).

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Client Setup](#client-setup)
  - [Basic Client](#basic-client)
  - [Context Manager](#context-manager)
  - [With API Token](#with-api-token)
  - [Custom Configuration](#custom-configuration)
- [Fetching Data](#fetching-data)
  - [OpenDOSM API](#opendosm-api)
  - [Data Catalogue API](#data-catalogue-api)
  - [Dataset Discovery](#dataset-discovery)
  - [Finding Dataset IDs](#finding-dataset-ids)
- [Query Builder](#query-builder)
  - [Exact Match Filters](#exact-match-filters)
  - [Partial Match Filters](#partial-match-filters)
  - [Numerical Range](#numerical-range)
  - [Sorting](#sorting)
  - [Date & Timestamp Ranges](#date--timestamp-ranges)
  - [Limiting Records](#limiting-records)
  - [Column Selection](#column-selection)
  - [Metadata Requests](#metadata-requests)
  - [Chaining Multiple Queries](#chaining-multiple-queries)
- [Response Format](#response-format)
  - [Default Response](#default-response)
  - [Response with Metadata](#response-with-metadata)
- [Pandas Integration](#pandas-integration)
  - [Basic DataFrame Conversion](#basic-dataframe-conversion)
  - [Auto Date Parsing](#auto-date-parsing)
  - [Working with Meta Responses](#working-with-meta-responses)
- [Error Handling](#error-handling)
  - [Exception Hierarchy](#exception-hierarchy)
  - [Handling Specific Errors](#handling-specific-errors)
  - [Rate Limiting & Retries](#rate-limiting--retries)
- [Logging](#logging)
- [API Reference](#api-reference)
- [Examples](#examples)
  - [CPI Analysis](#example-cpi-analysis)
  - [Fuel Price Tracker](#example-fuel-price-tracker)
  - [Population Dashboard Data](#example-population-dashboard-data)
  - [Dataset Discovery](#example-dataset-discovery)

---

## Installation

### Basic Install

```bash
pip install opendosm
```

### With Pandas Support

```bash
pip install opendosm[pandas]
```

### Development Install

```bash
git clone https://github.com/aldan-1/opendosm-py.git
cd opendosm-py
pip install -e ".[dev]"
```

### Requirements

- Python **3.9** or higher
- Dependencies (installed automatically):
  - `httpx >= 0.24.0`
  - `pydantic >= 2.0.0`
  - `pandas >= 1.5.0` *(optional, for DataFrame support)*

---

## Quick Start

```python
from opendosm import OpenDOSM

# Create a client
client = OpenDOSM()

# Fetch Consumer Price Index data
cpi_data = client.opendosm.cpi()
print(f"Got {len(cpi_data)} CPI records")
print(cpi_data[0])
# {'date': '2018-01-01', 'index': 118.1, 'division': 'overall'}

# Always close when done
client.close()
```

---

## Client Setup

### Basic Client

```python
from opendosm import OpenDOSM

client = OpenDOSM()

# ... use the client ...

client.close()  # Don't forget to close!
```

### Context Manager

The recommended approach — automatically closes the client:

```python
from opendosm import OpenDOSM

with OpenDOSM() as client:
    data = client.opendosm.get("cpi_core")
    # Client is automatically closed when leaving the block
```

### With API Token

If you have an API token (for higher rate limits), pass it at initialization:

```python
client = OpenDOSM(token="your-api-token-here")
```

> **How to get a token:** Email [dataterbuka@jdn.gov.my](mailto:dataterbuka@jdn.gov.my) with your name, email, and reason for requesting increased rate limits.

The token is sent as `Authorization: Token <your-token>` in every request header.

### Custom Configuration

```python
client = OpenDOSM(
    token="your-token",                          # Optional API token
    base_url="https://api.data.gov.my",          # Default base URL
    timeout=60.0,                                 # Request timeout in seconds (default: 30)
)
```

---

## Fetching Data

The SDK provides two API families through the client:

| Property | Endpoint | Description |
|---|---|---|
| `client.opendosm` | `/opendosm` | OpenDOSM statistical datasets (CPI, GDP, population, etc.) |
| `client.data_catalogue` | `/data-catalogue` | Broader data.gov.my datasets (fuel prices, etc.) |

### OpenDOSM API

#### Generic Access

Fetch any OpenDOSM dataset by its ID:

```python
data = client.opendosm.get("cpi_core")
data = client.opendosm.get("gdp_qtr_real")
data = client.opendosm.get("population_state")
```

#### Convenience Methods

Shortcuts for popular datasets:

```python
client.opendosm.cpi()          # Consumer Price Index (default: "cpi_core")
client.opendosm.gdp()          # Gross Domestic Product (default: "gdp_qtr_real")
client.opendosm.population()   # Population by State (default: "population_state")
client.opendosm.trade()        # External Trade (default: "trade_sitc_1d")
client.opendosm.labour()       # Labour Force Survey (default: "lfs_month")
```

Each convenience method accepts an optional `dataset_id` to use a variant:

```python
# Use a specific CPI variant
client.opendosm.cpi(dataset_id="cpi_state")
```

All methods also accept `query` and `meta` parameters:

```python
from opendosm import QueryBuilder

q = QueryBuilder().limit(10)
data = client.opendosm.cpi(query=q, meta=True)
```

### Data Catalogue API

Access the broader data.gov.my catalogue (280+ datasets):

```python
fuel = client.data_catalogue.get("fuelprice")
```

### Dataset Discovery

The SDK can dynamically discover all available datasets directly from the API — no hardcoded lists, always up to date:

```python
from opendosm import OpenDOSM

with OpenDOSM() as client:
    # List all 280+ datasets
    all_datasets = client.data_catalogue.list_datasets()
    print(f"{len(all_datasets)} datasets available")

    # Filter by category
    demo = client.data_catalogue.list_datasets(category="Demography")
    for ds in demo:
        print(f"  {ds.id}: {ds.title_en}")

    # Filter by source
    bnm = client.data_catalogue.list_datasets(source="BNM")

    # Search by keyword (matches id and title_en)
    results = client.data_catalogue.search("gdp")
    for ds in results:
        print(f"  {ds.id}: {ds.title_en} ({ds.frequency})")
```

Each result is a `DatasetInfo` object with these fields:

| Field | Description | Example |
|---|---|---|
| `id` | Dataset identifier for API calls | `"fuelprice"` |
| `title_en` | English title | `"Price of Petroleum & Diesel"` |
| `title_bm` | Malay title | `"Harga Minyak"` |
| `category_en` | Category | `"Prices"` |
| `subcategory_en` | Subcategory | `"Consumer Prices"` |
| `source` | Data source agency | `"KPDN, DOSM"` |
| `frequency` | Update frequency | `"WEEKLY"` |
| `geography` | Geographic scope | `"NATIONAL"` |
| `dataset_begin` | Earliest data year | `"2017"` |
| `dataset_end` | Latest data year | `"2025"` |

### Finding Dataset IDs

There are three ways to find dataset IDs:

1. **Use the SDK** (recommended): `client.data_catalogue.search("keyword")`
2. **OpenDOSM portal**: [open.dosm.gov.my/data-catalogue](https://open.dosm.gov.my/data-catalogue)
3. **data.gov.my**: [data.gov.my/data-catalogue](https://data.gov.my/data-catalogue)

On each web portal page, scroll to **"Sample OpenAPI query"** at the bottom to find the `id` value.

---

## Query Builder

The `QueryBuilder` provides a fluent, chainable interface for constructing API queries. Import it and build your query step by step:

```python
from opendosm import QueryBuilder

query = (
    QueryBuilder()
    .filter(state="Selangor")
    .sort("date", descending=True)
    .limit(50)
)

data = client.opendosm.get("cpi_core", query=query)
```

### Exact Match Filters

#### Case-Sensitive — `.filter()`

```python
# Single filter
query = QueryBuilder().filter(state="Selangor")
# API: ?filter=Selangor@state

# Multiple filters
query = QueryBuilder().filter(state="Selangor", division="01")
# API: ?filter=Selangor@state,01@division
```

#### Case-Insensitive — `.ifilter()`

```python
query = QueryBuilder().ifilter(state="selangor")
# API: ?ifilter=selangor@state
```

### Partial Match Filters

#### Case-Sensitive — `.contains()`

```python
query = QueryBuilder().contains(name="Kuala")
# API: ?contains=Kuala@name
```

#### Case-Insensitive — `.icontains()`

```python
query = QueryBuilder().icontains(name="kuala")
# API: ?icontains=kuala@name
```

### Numerical Range

Filter data within a numerical range (both bounds inclusive):

```python
# Full range
query = QueryBuilder().range("value", begin=10, end=100)
# API: ?range=value[10:100]

# Open-ended (no upper bound)
query = QueryBuilder().range("value", begin=50)
# API: ?range=value[50:]

# Open-ended (no lower bound)
query = QueryBuilder().range("value", end=200)
# API: ?range=value[:200]
```

### Sorting

```python
# Ascending (default)
query = QueryBuilder().sort("date")
# API: ?sort=date

# Descending
query = QueryBuilder().sort("date", descending=True)
# API: ?sort=-date

# Multiple columns
query = QueryBuilder().sort("state", "date", descending=False)
# API: ?sort=state,date

# Mixed directions (per-column)
query = QueryBuilder().sort("state", "date", descending=[False, True])
# API: ?sort=state,-date
```

### Date & Timestamp Ranges

#### Date Range (YYYY-MM-DD)

```python
# Both bounds
query = QueryBuilder().date_range("date", start="2023-01-01", end="2023-12-31")
# API: ?date_start=2023-01-01@date&date_end=2023-12-31@date

# Start only
query = QueryBuilder().date_range("date", start="2023-06-01")
# API: ?date_start=2023-06-01@date

# End only
query = QueryBuilder().date_range("date", end="2023-06-30")
# API: ?date_end=2023-06-30@date
```

#### Timestamp Range (YYYY-MM-DD HH:MM:SS)

```python
query = QueryBuilder().timestamp_range(
    "timestamp",
    start="2023-01-01 00:00:00",
    end="2023-12-31 23:59:59"
)
# API: ?timestamp_start=2023-01-01 00:00:00@timestamp
#      &timestamp_end=2023-12-31 23:59:59@timestamp
```

### Limiting Records

```python
query = QueryBuilder().limit(100)
# API: ?limit=100
```

If the total available records are fewer than the limit, all records are returned.

### Column Selection

#### Include Only Specific Columns

```python
query = QueryBuilder().include("date", "state", "value")
# API: ?include=date,state,value
```

#### Exclude Specific Columns

```python
query = QueryBuilder().exclude("id", "internal_code")
# API: ?exclude=id,internal_code
```

> **Note:** When both `.include()` and `.exclude()` are used together, `include` takes precedence.

### Metadata Requests

Request additional metadata alongside your data:

```python
query = QueryBuilder().with_meta()
# API: ?meta=true
```

Or via the `meta` parameter on any fetch method — see [Response with Metadata](#response-with-metadata).

### Chaining Multiple Queries

All query methods return `self`, so you can chain freely:

```python
query = (
    QueryBuilder()
    .filter(state="Selangor")
    .date_range("date", start="2023-01-01", end="2023-12-31")
    .sort("date", descending=True)
    .limit(50)
    .include("date", "state", "value")
)

data = client.opendosm.get("cpi_core", query=query)
```

You can also inspect what a query will produce:

```python
print(query.build())
# {'filter': 'Selangor@state', 'date_start': '2023-01-01@date',
#  'date_end': '2023-12-31@date', 'sort': '-date', 'limit': '50',
#  'include': 'date,state,value'}
```

---

## Response Format

### Default Response

By default, API calls return a **list of dictionaries** — each dict is one record:

```python
data = client.opendosm.cpi()
# type: list[dict[str, Any]]

print(data[0])
# {'date': '2018-01-01', 'index': 118.1, 'division': 'overall'}

print(len(data))
# 1358
```

### Response with Metadata

Pass `meta=True` to get an `APIResponse` object with both metadata and data:

```python
from opendosm import APIResponse

response = client.opendosm.get("cpi_core", meta=True)
# type: APIResponse

# Access metadata
print(response.meta)
# MetaInfo(...)

# Access data records
print(len(response.data))
# 1358

print(response.data[0])
# {'date': '2018-01-01', 'index': 118.1, 'division': 'overall'}
```

The `APIResponse` model has:
- `meta` — a `MetaInfo` object with information about the dataset and applied filters
- `data` — the list of record dictionaries

---

## Pandas Integration

> **Prerequisite:** Install with Pandas support: `pip install opendosm[pandas]`

### Basic DataFrame Conversion

```python
from opendosm import OpenDOSM

with OpenDOSM() as client:
    data = client.opendosm.cpi()
    df = client.to_dataframe(data)

    print(df.head())
    #          date  index division
    # 0  2018-01-01  118.1  overall
    # 1  2018-02-01  117.5  overall
    # ...

    print(df.shape)
    # (1358, 3)
```

### Auto Date Parsing

The SDK automatically detects and parses columns named `date`, `timestamp`, `year_month`, or `year` into proper `datetime64` types:

```python
df = client.to_dataframe(data)

print(df.dtypes)
# date        datetime64[ns]
# index              float64
# division            object
```

This lets you immediately use Pandas' datetime functionality:

```python
# Filter by year
df_2023 = df[df["date"].dt.year == 2023]

# Resample to quarterly
quarterly = df.set_index("date").resample("Q").mean()
```

### Working with Meta Responses

`to_dataframe()` also works with `APIResponse` objects:

```python
response = client.opendosm.get("cpi_core", meta=True)
df = client.to_dataframe(response)  # Extracts .data automatically
```

---

## Error Handling

### Exception Hierarchy

```
OpenDOSMError (base)
├── APIError (any non-200 response)
│   ├── RateLimitError (429 Too Many Requests)
│   ├── AuthenticationError (401 / 403)
│   └── NotFoundError (404)
└── InvalidQueryError (invalid query params, client-side)
```

All exceptions are importable from the top-level package:

```python
from opendosm import (
    OpenDOSMError,
    APIError,
    RateLimitError,
    AuthenticationError,
    NotFoundError,
    InvalidQueryError,
)
```

### Handling Specific Errors

```python
from opendosm import OpenDOSM, NotFoundError, RateLimitError, AuthenticationError

with OpenDOSM() as client:
    try:
        data = client.opendosm.get("nonexistent_dataset")

    except NotFoundError as e:
        print(f"Dataset not found: {e}")
        # [404] Resource not found

    except AuthenticationError as e:
        print(f"Auth failed: {e}")
        # [401] Authentication failed. Check your API token.

    except RateLimitError as e:
        print(f"Rate limited! Retry after: {e.retry_after}s")
        # [429] Rate limit exceeded. Please wait before retrying.

    except APIError as e:
        print(f"API error [{e.status_code}]: {e}")
        print(f"Error details: {e.errors}")
```

### Rate Limiting & Retries

The SDK automatically retries on **HTTP 429** (rate limit) responses with exponential backoff:

- **Max retries:** 3 (configurable)
- **Backoff:** 1s → 2s → 4s (doubles each retry)
- **Retry-After header:** Respected if provided by the API

If all retries are exhausted, a `RateLimitError` is raised.

```python
# The SDK handles this transparently:
data = client.opendosm.cpi()
# If rate limited, it waits and retries up to 3 times
```

To avoid rate limits entirely, [request an API token](#with-api-token).

---

## Logging

The SDK uses Python's built-in `logging` module under the `"opendosm"` logger name. Enable it to see request details and retry behavior:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Now you'll see:
# DEBUG:opendosm:GET /opendosm params={'id': 'cpi_core'} (attempt 1)
# WARNING:opendosm:Rate limited. Retrying in 1.0s …
```

For production, set to `WARNING` to only see retry warnings:

```python
logging.getLogger("opendosm").setLevel(logging.WARNING)
```

---

## API Reference

### `OpenDOSM` Class

| Method / Property | Description |
|---|---|
| `OpenDOSM(token=None, base_url=..., timeout=30.0)` | Create a new client |
| `.opendosm` | Access `OpenDOSMAPI` sub-client |
| `.data_catalogue` | Access `DataCatalogueAPI` sub-client |
| `.to_dataframe(data)` | Convert API data to Pandas DataFrame |
| `.close()` | Close the HTTP client |

### `OpenDOSMAPI` (via `client.opendosm`)

| Method | Description |
|---|---|
| `.get(dataset_id, query=None, *, meta=False)` | Fetch any dataset by ID |
| `.cpi(dataset_id="cpi_core", ...)` | Consumer Price Index |
| `.gdp(dataset_id="gdp_qtr_real", ...)` | Gross Domestic Product |
| `.population(dataset_id="population_state", ...)` | Population by State |
| `.trade(dataset_id="trade_sitc_1d", ...)` | External Trade |
| `.labour(dataset_id="lfs_month", ...)` | Labour Force Survey |

### `DataCatalogueAPI` (via `client.data_catalogue`)

| Method | Description |
|---|---|
| `.get(dataset_id, query=None, *, meta=False)` | Fetch any Data Catalogue dataset |
| `.list_datasets(*, category=None, source=None)` | List all datasets, optionally filtered |
| `.search(query)` | Search datasets by keyword (id/title) |

### `QueryBuilder`

| Method | Description |
|---|---|
| `.filter(**kwargs)` | Exact match, case-sensitive |
| `.ifilter(**kwargs)` | Exact match, case-insensitive |
| `.contains(**kwargs)` | Partial match, case-sensitive |
| `.icontains(**kwargs)` | Partial match, case-insensitive |
| `.range(column, begin=None, end=None)` | Numerical range filter |
| `.sort(*columns, descending=False)` | Sort by columns |
| `.date_range(column, start=None, end=None)` | Date filter (YYYY-MM-DD) |
| `.timestamp_range(column, start=None, end=None)` | Timestamp filter (YYYY-MM-DD HH:MM:SS) |
| `.limit(n)` | Max records to return |
| `.include(*columns)` | Include only these columns |
| `.exclude(*columns)` | Exclude these columns |
| `.with_meta(enabled=True)` | Request response metadata |
| `.build()` | Return params as `dict[str, str]` |

### Response Models

| Model | Fields | Description |
|---|---|---|
| `APIResponse` | `.meta`, `.data` | Structured response from `meta=True` |
| `DatasetInfo` | `.id`, `.title_en`, `.category_en`, ... | Dataset metadata from `list_datasets()` |
| `MetaInfo` | *(dynamic)* | Metadata about the dataset |
| `ErrorResponse` | `.status`, `.errors` | Error structure from the API |

### Exceptions

| Exception | When Raised |
|---|---|
| `OpenDOSMError` | Base exception for all SDK errors |
| `APIError` | Any non-200 HTTP response |
| `RateLimitError` | HTTP 429 after exhausting retries |
| `AuthenticationError` | HTTP 401 or 403 |
| `NotFoundError` | HTTP 404 (invalid dataset ID) |
| `InvalidQueryError` | Invalid query parameters (client-side) |

---

## Examples

### Example: CPI Analysis

```python
from opendosm import OpenDOSM, QueryBuilder

with OpenDOSM() as client:
    # Fetch CPI data for 2023, sorted by date
    query = (
        QueryBuilder()
        .date_range("date", start="2023-01-01", end="2023-12-31")
        .filter(division="overall")
        .sort("date")
    )

    data = client.opendosm.cpi(query=query)
    df = client.to_dataframe(data)

    print("CPI Trend in 2023:")
    print(df[["date", "index"]].to_string(index=False))

    print(f"\nAverage CPI: {df['index'].mean():.1f}")
    print(f"Min: {df['index'].min():.1f} | Max: {df['index'].max():.1f}")
```

### Example: Fuel Price Tracker

```python
from opendosm import OpenDOSM, QueryBuilder

with OpenDOSM() as client:
    # Get recent fuel prices (Data Catalogue API)
    query = (
        QueryBuilder()
        .sort("date", descending=True)
        .limit(10)
        .include("date", "ron95", "ron97", "diesel")
    )

    data = client.data_catalogue.get("fuelprice", query=query)
    df = client.to_dataframe(data)

    print("Latest Fuel Prices (MYR/litre):")
    print(df.to_string(index=False))
```

### Example: Population Dashboard Data

```python
from opendosm import OpenDOSM, QueryBuilder

with OpenDOSM() as client:
    # Population by state, latest year
    query = (
        QueryBuilder()
        .sort("date", descending=True)
        .limit(16)  # 16 states
    )

    response = client.opendosm.population(query=query, meta=True)

    print(f"Dataset metadata: {response.meta}")
    print(f"Records: {len(response.data)}")

    df = client.to_dataframe(response)
    print(df[["date", "state", "population"]].to_string(index=False))
```

### Example: Dataset Discovery

```python
from opendosm import OpenDOSM

with OpenDOSM() as client:
    # What categories are available?
    all_ds = client.data_catalogue.list_datasets()
    categories = sorted(set(ds.category_en for ds in all_ds))
    print("Available categories:")
    for cat in categories:
        count = sum(1 for ds in all_ds if ds.category_en == cat)
        print(f"  {cat} ({count} datasets)")

    # Find all GDP-related datasets
    gdp = client.data_catalogue.search("gdp")
    print(f"\n{len(gdp)} GDP datasets:")
    for ds in gdp:
        print(f"  {ds.id}: {ds.title_en}")

    # Get data from a discovered dataset
    data = client.data_catalogue.get(gdp[0].id, limit=5)
    print(f"\nFirst 5 records from {gdp[0].id}:")
    for row in data:
        print(f"  {row}")
```

---

## Resources

- **API Documentation**: [developer.data.gov.my](https://developer.data.gov.my/)
- **OpenDOSM Portal**: [open.dosm.gov.my](https://open.dosm.gov.my/)
- **Dataset Catalogue**: [data.gov.my/data-catalogue](https://data.gov.my/data-catalogue)
- **Source Code**: [github.com/aldan-1/opendosm-py](https://github.com/aldan-1/opendosm-py)
- **Report Issues**: [github.com/aldan-1/opendosm-py/issues](https://github.com/aldan-1/opendosm-py/issues)
