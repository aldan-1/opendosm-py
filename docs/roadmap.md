# Roadmap — opendosm-py

> All versions are Alpha (`Development Status :: 3 - Alpha`) until v1.0.0.
> Last updated: 2026-07-31

---

## Current: v0.1.2 (released 2026-07-31)

✅ OpenDOSM API  
✅ Data Catalogue API  
✅ QueryBuilder (all 13 query parameters)  
✅ Pydantic v2 response models  
✅ 104 unit tests (mocked HTTP) + 15 live integration tests  
✅ CI/CD (4 Python versions, ruff, mypy, pytest) — **passing**  
✅ PyPI publishing (trusted publishing)  
✅ Pandas integration (optional extra)  
✅ Registry pattern for convenience methods (70 → 20 lines)  
✅ Single version source (`_version.py`) with hatchling dynamic version  
✅ `max_retries` exposed on `OpenDOSM` client  
✅ Dynamic User-Agent from `__version__`  
✅ `uv.lock` committed for reproducible dev environments  
✅ `docs/` directory (architecture, api-coverage, roadmap, session-log)  

---

## Next Releases

### v0.2.0 — Weather API + Infra Polish 🟢 (Est. ~2.5 days)

```
client.weather.forecast(location_id="Ds001")
client.weather.warning()
client.weather.earthquake()
```

**Feature:**
- Same JSON pattern as existing APIs — reuses `QueryBuilder`
- Supports nested field `__` syntax (e.g. `location__location_id`)
- Location ID prefixes: St (State), Ds (District), Tn (Town), Rc (Recreation), Dv (Division)
- Update: forecast daily, warnings as required
- **New file:** `src/opendosm/api/weather.py`

**Infra (bundled with this release):**
- Split CI lint job from test matrix (saves ~75% runner minutes)
- Broaden HTTP retry: add 408, 409, 5xx + jitter + multi-format `Retry-After` parsing
- Attach `request_id` to error classes (Stripe/OpenAI pattern)

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

### v0.5.0 — Performance & Async 🟡 (Est. ~3 days)

```
cache = client.cache  # In-memory TTL cache
async with AsyncOpenDOSM() as client: ...
```

- **In-memory TTL cache** for `list_datasets()` and catalogue lookups — ~10x speedup for notebook workflows
- **`AsyncOpenDOSM` client** — first government open-data SDK with async support
- Full `uv` migration in CI (`astral-sh/setup-uv`, `uv sync --group dev`)
- **New files:** `src/opendosm/cache.py`, `src/opendosm/async_client.py`
- ~~Pipeline & Export~~ (deprioritized — caching + async offer higher value per effort)

---

## v1.0.0 — Production Polish (Est. ~5 days)

| Feature | Priority |
|---------|----------|
| `release-please` auto-changelog + version bumps | High |
| `justfile` task runner (`just lint`, `just test`, `just build`) | High |
| Windows CI matrix (Malaysian users are Windows-first) | High |
| `SECURITY.md` + CodeQL scanning | High |
| Sphinx/mkdocs documentation site | Medium |
| Inline-snapshot or VCR testing (betamax/vcrpy) | Medium |
| `--cov-fail-under=80` in CI | Low |
| Property-based tests with Hypothesis | Low |
| Pipeline & Export (bulk CSV/SQLite export) | Low |

---

## Deprioritized

| Item | Original Target | Reason |
|------|----------------|--------|
| Pipeline & Export (`[pipeline]` extra) | v0.5.0 | Caching + async found to be higher user value in research |

---

## Dependency Timeline

| Extra | Added In | Deps |
|-------|----------|------|
| `[dev]` | v0.1.0 ✅ | pytest, ruff, mypy, pandas, pandas-stubs, numpy (pinned <2.5) |
| `[pandas]` | v0.1.0 ✅ | pandas |
| `[realtime]` | v0.4.0 ❌ | gtfs-realtime-bindings |
| `[pipeline]` | v1.0.0+ ❌ | tqdm, pandas (deprioritized) |
