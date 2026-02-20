# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-20

### Added

- Initial release
- `OpenDOSM` client class with OpenDOSM and Data Catalogue API support
- Fluent `QueryBuilder` for filtering, sorting, and pagination
- Pydantic response models with validation
- Automatic retry on rate-limit (429) responses
- Optional Pandas DataFrame integration (`pip install opendosm[pandas]`)
