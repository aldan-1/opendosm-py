# opendosm 🇲🇾

[![CI](https://github.com/aldan-1/opendosm-py/actions/workflows/ci.yml/badge.svg)](https://github.com/aldan-1/opendosm-py/actions)
[![PyPI](https://img.shields.io/pypi/v/opendosm)](https://pypi.org/project/opendosm/)
[![Python](https://img.shields.io/pypi/pyversions/opendosm)](https://pypi.org/project/opendosm/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Pythonic SDK for Malaysia's **[data.gov.my Open API](https://developer.data.gov.my/)** — providing clean access to OpenDOSM statistical datasets with optional Pandas integration.

## Features

- 🔍 **Fluent QueryBuilder** — filter, sort, paginate, and select columns with a chainable API
- 🗂️ **Dataset discovery** — `list_datasets()` and `search()` to find any of the 280+ available datasets
- 📊 **Pandas integration** — `.to_dataframe()` with automatic date parsing
- ⚡ **Smart retries** — automatic exponential backoff on rate limits (429)
- 🔐 **Token auth** — optional API token for higher rate limits
- 🧩 **Typed** — full type hints and Pydantic response models
- 📦 **Zero config** — works out of the box, no API key required

## Installation

```bash
pip install opendosm

# With Pandas support
pip install opendosm[pandas]
```

## Quick Start

```python
from opendosm import OpenDOSM

client = OpenDOSM()

# Fetch CPI data
cpi_data = client.opendosm.cpi()

# Fetch population data
population = client.opendosm.population()

# Fetch any dataset by ID
data = client.opendosm.get("gdp_qtr_real")

# Don't forget to close
client.close()
```

### Context Manager

```python
with OpenDOSM() as client:
    data = client.opendosm.get("cpi_core")
```

### With API Token

```python
client = OpenDOSM(token="your-api-token")
```

## Filtering & Queries

Use the fluent `QueryBuilder` to construct queries:

```python
from opendosm import OpenDOSM, QueryBuilder

client = OpenDOSM()

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

### Available Query Methods

| Method | Description | Example |
|---|---|---|
| `.filter(**kwargs)` | Exact match (case-sensitive) | `.filter(state="Selangor")` |
| `.ifilter(**kwargs)` | Exact match (case-insensitive) | `.ifilter(state="selangor")` |
| `.contains(**kwargs)` | Partial match (case-sensitive) | `.contains(name="Kuala")` |
| `.icontains(**kwargs)` | Partial match (case-insensitive) | `.icontains(name="kuala")` |
| `.range(col, begin, end)` | Numerical range | `.range("value", 10, 100)` |
| `.sort(*cols, descending)` | Sort results | `.sort("date", descending=True)` |
| `.date_range(col, start, end)` | Date filter (YYYY-MM-DD) | `.date_range("date", start="2023-01-01")` |
| `.timestamp_range(col, start, end)` | Timestamp filter (YYYY-MM-DD HH:MM:SS) | `.timestamp_range("ts", start="2023-01-01 00:00:00")` |
| `.limit(n)` | Max records | `.limit(100)` |
| `.include(*cols)` | Include columns only | `.include("date", "value")` |
| `.exclude(*cols)` | Exclude columns | `.exclude("id")` |
| `.with_meta()` | Include metadata | `.with_meta()` |

> **Note:** When both `.include()` and `.exclude()` are used, `include` takes precedence.

## Pandas Integration

```python
from opendosm import OpenDOSM

client = OpenDOSM()

# Fetch and convert to DataFrame
data = client.opendosm.cpi()
df = client.to_dataframe(data)

print(df.head())
print(df.dtypes)  # Date columns auto-parsed!
```

## Convenience Methods

The SDK provides shortcuts for popular datasets:

```python
client.opendosm.cpi()          # Consumer Price Index (default: "cpi_core")
client.opendosm.gdp()          # Gross Domestic Product (default: "gdp_qtr_real")
client.opendosm.population()   # Population by State (default: "population_state")
client.opendosm.trade()        # External Trade (default: "trade_sitc_1d")
client.opendosm.labour()       # Labour Force Survey (default: "lfs_month")
```

All accept an optional `query` parameter and custom `dataset_id`.

## Data Catalogue API

Access the broader data.gov.my catalogue (280+ datasets):

```python
# Fetch a specific dataset
data = client.data_catalogue.get("fuelprice")

# Discover available datasets (live from API, always up to date)
all_datasets = client.data_catalogue.list_datasets()

# Filter by category or source
demo = client.data_catalogue.list_datasets(category="Demography")
dosm = client.data_catalogue.list_datasets(source="DOSM")

# Search by keyword across IDs and titles
gdp_datasets = client.data_catalogue.search("gdp")
for ds in gdp_datasets:
    print(f"{ds.id}: {ds.title_en}")
```

## Error Handling

```python
from opendosm import OpenDOSM, RateLimitError, NotFoundError

client = OpenDOSM()

try:
    data = client.opendosm.get("nonexistent_dataset")
except NotFoundError:
    print("Dataset not found!")
except RateLimitError:
    print("Rate limited — try again later or use an API token")
```

## Development

```bash
# Clone and install in dev mode
git clone https://github.com/aldan-1/opendosm-py.git
cd opendosm-py
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linter
ruff check src/ tests/

# Type check
mypy src/opendosm/
```

## License

MIT — see [LICENSE](LICENSE).

## Links

- **API Docs**: [developer.data.gov.my](https://developer.data.gov.my/)
- **OpenDOSM Portal**: [open.dosm.gov.my](https://open.dosm.gov.my/)
- **Dataset Catalogue**: [open.dosm.gov.my/data-catalogue](https://open.dosm.gov.my/data-catalogue)
