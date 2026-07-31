# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-07-31

### Added

- `max_retries` parameter on `OpenDOSM` client (previously only on internal `HTTPClient`)
- `docs/` directory with architecture, API coverage, and roadmap documentation
- `test_sdk_manual.py` in version control (15 live integration tests, previously untracked)
- `uv.lock` for reproducible development environments
- `knowledge base/` folder to `.gitignore` (personal development notes)

### Changed

- Refactored 5 convenience methods (`cpi`, `gdp`, `population`, `trade`, `labour`) into a registry pattern — ~70 lines → ~20 lines, identical API
- Version source consolidated into `_version.py` — `__init__.py`, `http.py`, and `pyproject.toml` all read from one place; `pyproject.toml` now uses `dynamic = ["version"]` via hatchling
- User-Agent header now dynamically reflects `__version__` (was hardcoded to `0.1.0`)

### Fixed

- README no longer claims tokens give "higher rate limits" — all tiers are 4 req/min per official docs
- `test_sdk_manual.py`: 23 ruff violations fixed (21 auto-fixed, 2 manual: `assert False` → `raise AssertionError`)
- `test_sdk_manual.py`: renamed helper `test()` → `run_test()` to prevent pytest auto-collection as a test item
- CI mypy failure on numpy 2.5+ stubs: pinned `numpy>=1.24,<2.5` in dev extras (numpy 2.5+ stubs use Python 3.12 `type` syntax incompatible with `python_version = "3.10"`)

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