┌─────────────────────────────────────────────────────────────────────────────┐
│                         opendosm-py v0.1.2 — System Architecture            │
│                         data.gov.my Open API Python SDK                     │
└─────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
                              LAYER 0: USER CODE
═══════════════════════════════════════════════════════════════════════════════

    from opendosm import OpenDOSM, QueryBuilder

    client = OpenDOSM(max_retries=5)            # Facade — single entry point
    data   = client.opendosm.cpi()              # Convenience method
    df     = client.to_dataframe(data)           # Pandas integration

                                    │
                                    ▼
═══════════════════════════════════════════════════════════════════════════════
                         LAYER 1: PUBLIC API (__init__.py)
═══════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  __init__.py           Exports: OpenDOSM, QueryBuilder,                 │
  │  (11 public symbols)   APIResponse, DatasetInfo, MetaInfo,              │
  │                        OpenDOSMError, APIError, RateLimitError,         │
  │                        AuthenticationError, NotFoundError,              │
  │                        InvalidQueryError, __version__                   │
  └─────────────────────────────────────────────────────────────────────────┘
          │                    │                        │
          ▼                    ▼                        ▼
  ┌───────────────┐   ┌───────────────┐    ┌───────────────────────┐
  │  _version.py  │   │   client.py   │    │    exceptions.py      │
  │  __version__  │   │  OpenDOSM     │    │  OpenDOSMError (base) │
  │  ="0.1.2"     │   │  (Facade)     │    │   ├─ APIError         │
  │               │   │               │    │   │  ├─RateLimitError │
  │  ← imported   │   │ .opendosm ────┼───▶│   │  ├─AuthError     │
  │    by http.py │   │ .data_catalogue┼───▶│   │  └─NotFoundError │
  │    & init.py  │   │ .to_dataframe()│    │   └─InvalidQueryError│
  └───────────────┘   │ .to_sql() [TBD]│    └───────────────────────┘
                      │ .close()       │
                      │ __enter/exit__ │
                      └───┬───────┬───┘
                          │       │
            ┌─────────────┘       └─────────────┐
            ▼                                    ▼
═══════════════════════════════════════════════════════════════════════════════
                      LAYER 2: API WRAPPERS (api/)
═══════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                        api/base.py — BaseAPI                            │
  │                        Template Method pattern                          │
  │                                                                         │
  │  _get(dataset_id, query?, meta?, **extra)                               │
  │      │                                                                  │
  │      ├── params = {"id": dataset_id}                                    │
  │      ├── params.update(query.build())   # ← QueryBuilder integration    │
  │      ├── params.update(extra_params)                                    │
  │      ├── raw = self._http.get(path, params)  # → http.py               │
  │      └── meta=True? → APIResponse.model_validate(raw) : cast(list, raw) │
  └─────────────────────────────────────────────────────────────────────────┘
                    │                              │
          ┌─────────┴─────────┐          ┌─────────┴─────────┐
          ▼                   ▼          ▼                   ▼
  ┌──────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
  │ api/opendosm.py  │ │api/data_catalogue.py │ │ api/weather.py       │
  │ OpenDOSMAPI      │ │DataCatalogueAPI      │ │ [v0.2.0 planned]     │
  │ path="/opendosm" │ │path="/data-catalogue"│ │ path="/weather"      │
  │                  │ │                      │ │                      │
  │ .get(id) ← Base  │ │ .get(id) ← Base      │ │ .forecast(loc_id)    │
  │ .cpi()           │ │ .list_datasets()     │ │ .warning()           │
  │ .gdp()           │ │  ├─ category filter  │ │ .earthquake()        │
  │ .population()    │ │  └─ source filter    │ │                      │
  │ .trade()         │ │ .search(query)       │ │  CONVENIENCE = {     │
  │ .labour()        │ │                      │ │   cpi: "cpi_core",   │
  │                  │ │  _CONVENIENCE dict   │ │   gdp: "gdp_qtr...", │
  │  Registry pattern│ │  (dynamic method     │ │   ...                │
  │  generates 5     │ │   generation)        │ │  }                   │
  │  methods from    │ │                      │ │                      │
  │  _CONVENIENCE    │ │                      │ │                      │
  └──────┬───────────┘ └──────────┬───────────┘ └──────────────────────┘
         │                        │
         └────────────┬───────────┘
                      ▼
═══════════════════════════════════════════════════════════════════════════════
                       LAYER 3: HTTP TRANSPORT (http.py)
═══════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                         HTTPClient (Adapter)                            │
  │                                                                         │
  │  ┌─────────────────────────────────────────────────────────────────┐    │
  │  │ Constructor                                                    │    │
  │  │   base_url="https://api.data.gov.my"                           │    │
  │  │   token → Authorization: Token {token}                         │    │
  │  │   User-Agent: opendosm-py/{__version__}   ← dynamic            │    │
  │  │   timeout=30s, max_retries=3                                   │    │
  │  └─────────────────────────────────────────────────────────────────┘    │
  │                                                                         │
  │  get(path, params)                                                      │
  │      │                                                                  │
  │      ▼                                                                  │
  │  ┌─────────────────────────────────────────────────────────────────┐    │
  │  │ httpx.Client.get(path, params=params)                          │    │
  │  │     │                                                          │    │
  │  │     ├── 200 → return response.json()                           │    │
  │  │     ├── 429 → retry with exponential backoff + Retry-After     │    │
  │  │     │         backoff: 1s → 2s → 4s (× max_retries)           │    │
  │  │     │         exhausted → raise RateLimitError(retry_after)    │    │
  │  │     ├── 401/403 → raise AuthenticationError                    │    │
  │  │     ├── 404     → raise NotFoundError                          │    │
  │  │     └── 5xx     → raise APIError(status_code, errors)          │    │
  │  └─────────────────────────────────────────────────────────────────┘    │
  └─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  api.data.gov.my    │
                         │  ┌────────────────┐ │
                         │  │ /opendosm      │ │  ← Statistical data
                         │  │ /data-catalogue│ │  ← Dataset discovery
                         │  │ /weather       │ │  ← [v0.2.0 planned]
                         │  │ /gtfs-static   │ │  ← [v0.3.0 planned]
                         │  │ /gtfs-realtime │ │  ← [v0.4.0 planned]
                         │  └────────────────┘ │
                         │  Rate: 4 req/min     │
                         └─────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
                        LAYER 4: DATA MODELS (models.py)
═══════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Pydantic v2 models — extra="allow" (forward-compatible)                │
  │                                                                         │
  │  ┌──────────────┐    ┌────────────────┐    ┌──────────────────────┐     │
  │  │  APIResponse │    │  DatasetInfo   │    │  ErrorResponse        │     │
  │  │  ────────────│    │  ──────────────│    │  ──────────────────── │     │
  │  │  meta: Meta  │    │  id            │    │  status: int          │     │
  │  │  data: list  │    │  title_en      │    │  errors: list[Any]    │     │
  │  └──────────────┘    │  title_bm      │    └──────────────────────┘     │
  │                      │  category_en   │                                 │
  │  ┌──────────────┐    │  source        │   ┌──────────────────────┐     │
  │  │  MetaInfo    │    │  frequency     │   │  ErrorDetail          │     │
  │  │  ─────────── │    │  geography     │   │  ──────────────────── │     │
  │  │  (any keys)  │    │  dataset_begin │   │  message: str         │     │
  │  │  extra=allow │    │  dataset_end   │   └──────────────────────┘     │
  │  └──────────────┘    └────────────────┘                                 │
  └─────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
                       LAYER 5: QUERY BUILDER (query.py)
═══════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  QueryBuilder — Fluent Builder Pattern                                  │
  │                                                                         │
  │  q = (QueryBuilder()                                                    │
  │       .filter(state="Selangor")            → "Selangor@state"           │
  │       .date_range("date", "2023-01","2023-12") → date_start/date_end    │
  │       .sort("date", descending=True)       → "-date"                    │
  │       .limit(50)                           → "50"                       │
  │       .include("date","value"))            → "date,value"               │
  │                                                                         │
  │  ┌──────────────────────────────────────────────────────────────────┐   │
  │  │  Row Filters       │  Sort/Paging    │  Column Selection         │   │
  │  │  ───────────────── │  ───────────────│  ──────────────────────── │   │
  │  │  .filter(**kw)     │  .sort(*cols)   │  .include(*cols)          │   │
  │  │  .ifilter(**kw)    │  .limit(n)      │  .exclude(*cols)          │   │
  │  │  .contains(**kw)   │  .date_range()  │  .with_meta(bool)         │   │
  │  │  .icontains(**kw)  │  .timestamp_rng │                           │   │
  │  │  .range(col,b,e)   │                 │                           │   │
  │  └──────────────────────────────────────────────────────────────────┘   │
  │                                                                         │
  │  .build() → dict[str, str]   (materialise lazily)                       │
  └─────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
                     LAYER 6: INTEGRATIONS (integrations/)
═══════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  integrations/pandas.py                                                 │
  │                                                                         │
  │  to_dataframe(data)                                                     │
  │      │                                                                  │
  │      ├── isinstance(data, APIResponse) → data.data                      │
  │      ├── isinstance(data, list[BaseModel]) → [m.model_dump() for ...]   │
  │      ├── isinstance(data, list) → data                                  │
  │      └── else → TypeError("Expected list or APIResponse")               │
  │                                                                         │
  │  _infer_dates(df):                                                      │
  │      date/timestamp/year_month/year → pd.to_datetime(coerce)            │
  │                                                                         │
  │  _coerce_numerics(df):                                                  │
  │      object columns with >50% numeric → pd.to_numeric(coerce)           │
  └─────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
                        LAYER 7: TESTING (tests/)
═══════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  104 unit tests (mocked HTTP)  +  15 live integration tests             │
  │                                                                         │
  │  ┌───────────────────┐ ┌──────────────────────┐ ┌──────────────────┐   │
  │  │ test_client.py  7 │ │ test_exceptions.py 12│ │ test_http.py   14│   │
  │  │ test_models.py  7 │ │ test_query.py      27│ │ test_pandas.py 11│   │
  │  │ test_opendosm     │ │ test_data_catalogue  │ │ test_sdk_manual  │   │
  │  │        _api.py 10 │ │          _api.py  16│ │           .py  15│   │
  │  └───────────────────┘ └──────────────────────┘ └──────────────────┘   │
  │                                                                         │
  │  conftest.py → mock_client fixture (HTTPClient with httpx_mock)         │
  │  All HTTP calls mocked via pytest-httpx — zero network in unit tests    │
  └─────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
                       LAYER 8: CI/CD (.github/workflows/)
═══════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────┐          ┌──────────────────────────────┐
  │  ci.yml                 │          │  publish.yml                 │
  │  ───────────────────── │          │  ─────────────────────────── │
  │  on: push/PR to master │          │  on: GitHub Release          │
  │                         │          │                              │
  │  Matrix:                │          │  python -m build             │
  │    3.10  3.11  3.12  3.13         │  pypa/gh-action-pypi-publish │
  │                         │          │  (trusted publishing / OIDC) │
  │  Steps:                 │          │                              │
  │    pip install -e .[dev]│          │  Trigger:                    │
  │    ruff check           │          │    gh release create vX.Y.Z  │
  │    mypy --strict        │          │    → auto-builds + uploads   │
  │    pytest --cov         │          └──────────────────────────────┘
  └─────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
                     COMPLETE DATA FLOW (End-to-End)
═══════════════════════════════════════════════════════════════════════════════

  User Code
      │
      ▼
  OpenDOSM(max_retries=5)                         ┌──────────────────────┐
      │                                            │  DESIGN PATTERNS     │
      ├── .opendosm ──→ OpenDOSMAPI              │  ─────────────────── │
      │      │           .get("cpi_core")          │  Facade:    client   │
      │      │           .cpi() / .gdp() / ...     │  Template:  BaseAPI  │
      │      │           ._get(id, query, meta)     │  Builder:   Query   │
      │      │                                      │  Adapter:   HTTP    │
      │      ├── QueryBuilder.build() → params     └──────────────────────┘
      │      │
      │      └── HTTPClient.get("/opendosm", params)
      │              │
      │              ├── httpx.Client → api.data.gov.my
      │              │       │
      │              │       ├── 200 → response.json()
      │              │       ├── 429 → retry (×3, backoff 1s→2s→4s)
      │              │       └── 4xx/5xx → raise typed exception
      │              │
      │              └── returns: list[dict] or APIResponse
      │
      ├── .data_catalogue → DataCatalogueAPI
      │      │
      │      ├── .get("fuelprice")       → same flow as above
      │      ├── .list_datasets()        → fetches ?id=datasets
      │      │      ├── category= filter → client-side filter
      │      │      └── source= filter   → client-side filter
      │      └── .search("gdp")          → list_datasets() + Python filter
      │
      └── .to_dataframe(data)
              │
              ├── list[dict] → pd.DataFrame
              ├── APIResponse → pd.DataFrame(data.data)
              ├── list[BaseModel] → pd.DataFrame([m.model_dump()])
              ├── _infer_dates()  → date columns → datetime64
              └── _coerce_numerics() → object(numeric) → float64
