# Roadmap — opendosm-py

> All versions are Alpha (`Development Status :: 3 - Alpha`) until v1.0.0.

---

## Current: v0.1.1 (released 2026-03-02)

✅ OpenDOSM API  
✅ Data Catalogue API  
✅ QueryBuilder (all 13 query parameters)  
✅ Pydantic v2 response models  
✅ 104 unit tests (mocked HTTP)  
✅ 15 live integration tests  
✅ CI/CD (4 Python versions, ruff, mypy, pytest)  
✅ PyPI publishing (trusted publishing)  
✅ Pandas integration (optional extra)  

---

## Next Releases

### v0.2.0 — Weather API 🟢 (Est. ~2 days)

```
client.weather.forecast(location_id="Ds001")
client.weather.warning()
client.weather.earthquake()
```

- Same JSON pattern as existing APIs — reuses `QueryBuilder`
- Supports nested field `__` syntax (e.g. `location__location_id`)
- Location ID prefixes: St (State), Ds (District), Tn (Town), Rc (Recreation), Dv (Division)
- Update: forecast daily, warnings as required
- **New file:** `src/opendosm/api/weather.py`

### v0.3.0 — GTFS Static 🟡 (Est. ~3 days)

```
client.transport.gtfs_static("ktmb")
client.transport.gtfs_static("prasarana", category="rapid-rail-kl")
```

- Binary ZIP download + extraction (new HTTP handler path)
- 11 operators: KTMB, Prasarana (5 categories), BAS.MY (9 cities)
- Parses GTFS CSV tables (routes, stops, stop_times, trips, calendar)
- Refresh: daily at 4am recommended
- **New infra:** Binary download support in `http.py`

### v0.4.0 — GTFS Realtime 🔴 (Est. ~5 days)

```
client.transport.vehicle_position("ktmb")
```

- Protobuf parsing via `gtfs-realtime-bindings`
- New `[realtime]` extra in `pyproject.toml`
- Vehicle positions (trip updates + service alerts planned upstream for 2026)
- Updates every 30 seconds
- **New file:** `src/opendosm/api/gtfs_realtime.py`

### v0.5.0 — Pipeline & Export 🟡 (Est. ~2 days)

```
pipeline = client.pipeline()
pipeline.export_sqlite("data.db")
pipeline.export_csv("output/")
```

- Bulk download across multiple datasets
- CSV / SQLite export options
- Progress bars via `tqdm`
- New `[pipeline]` extra

---

## v1.0.0 — Stable Release 🟡 (Est. ~4 days)

| Feature | Priority |
|---------|----------|
| Async client (`AsyncOpenDOSM` via `httpx.AsyncClient`) | High |
| TTL caching for `list_datasets()` | Medium |
| Sphinx/mkdocs documentation site | Medium |
| `--cov-fail-under=80` in CI | Low |
| Property-based tests with Hypothesis | Low |

---

## Dependency Timeline

| Extra | Added In | Deps |
|-------|----------|------|
| `[dev]` | v0.1.0 ✅ | pytest, ruff, mypy, pandas |
| `[pandas]` | v0.1.0 ✅ | pandas |
| `[realtime]` | v0.4.0 ❌ | gtfs-realtime-bindings |
| `[pipeline]` | v0.5.0 ❌ | tqdm, pandas |
