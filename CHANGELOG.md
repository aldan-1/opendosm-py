# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-06-11

### Added

- `max_retries` parameter on `OpenDOSM` client (previously only on internal `HTTPClient`)

### Changed

- Refactored 5 convenience methods (`cpi`, `gdp`, `population`, `trade`, `labour`) into a registry pattern — ~70 lines → ~20 lines, identical API
- Version source consolidated into `_version.py` — `__init__.py`, `http.py`, and `pyproject.toml` all read from one place
- User-Agent header now dynamically reflects `__version__` (was hardcoded to `0.1.0`)

### Fixed

- README no longer claims tokens give "higher rate limits" — all tiers are 4 req/min per official docs

## [0.1.1] - 2026-06-11

### Fixed

- Sync `__version__` in `__init__.py` to match `pyproject.toml` (was `0.1.0`)

## [0.1.0] - 2026-02-20

### Added

- Initial release
- `OpenDOSM` client class with OpenDOSM and Data Catalogue API support
- Fluent `QueryBuilder` for filtering, sorting, and pagination
- Pydantic response models with validation
- Automatic retry on rate-limit (429) responses
- Optional Pandas DataFrame integration (`pip install opendosm[pandas]`)
- Dataset discovery via `list_datasets()` and `search()` methods
- `DatasetInfo` model for structured dataset metadata
- Pandas support for `list[DatasetInfo]` conversion and numeric coercion
- Convenience methods: `cpi()`, `gdp()`, `population()`, `trade()`, `labour()`
- 104 unit tests with full mocked coverage
