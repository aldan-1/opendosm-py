# API Coverage — opendosm-py

Comparison of the current SDK (v0.1.1) against all [data.gov.my](https://developer.data.gov.my/) API endpoints.

---

## Static APIs (JSON — ✅ Fully Implemented)

### 1. OpenDOSM API — `api.data.gov.my/opendosm`

| Feature | Status |
|---------|--------|
| `GET ?id=<dataset_id>` | ✅ `api.get("cpi_core")` |
| Query filters (filter, ifilter, contains, icontains) | ✅ Via `QueryBuilder` |
| Range filter | ✅ `.range("value", 10, 100)` |
| Sort | ✅ `.sort("date", descending=True)` |
| Date/timestamp range | ✅ `.date_range()`, `.timestamp_range()` |
| Limit | ✅ `.limit(100)` |
| Include/exclude columns | ✅ `.include()`, `.exclude()` |
| `?meta=true` | ✅ Returns `APIResponse` with `MetaInfo` |
| Convenience methods | ✅ `cpi()`, `gdp()`, `population()`, `trade()`, `labour()` |
| Dataset discovery | ✅ `list_datasets()`, `search()` |
| Pandas integration | ✅ `to_dataframe()` with date parsing |

### 2. Data Catalogue API — `api.data.gov.my/data-catalogue`

| Feature | Status |
|---------|--------|
| `GET ?id=<dataset_id>` | ✅ `data_catalogue.get("fuelprice")` |
| All query parameters | ✅ Same `QueryBuilder` works |
| `?meta=true` | ✅ Returns `APIResponse` |
| Dataset discovery | ✅ `list_datasets()`, `search()` |

---

## Realtime APIs (JSON — ❌ Not Started)

### 3. Weather API — `api.data.gov.my/weather/`

JSON format with standard query parameters — same pattern as OpenDOSM, easiest to implement next.

| Feature | Status |
|---------|--------|
| `GET /weather/forecast` | ❌ 7-day forecast by location |
| `GET /weather/warning` | ❌ Weather alerts (storms, floods) |
| `GET /weather/warning/earthquake` | ❌ Earthquake data (lat, lon, depth, mag) |
| Nested field query (`__` syntax) | ❌ e.g. `location__location_id` |
| Location ID prefixes (St, Ds, Tn, Rc, Dv) | ❌ |

**Update frequency:** Forecast — daily. Warnings — as required.

---

## Realtime APIs (Binary — ❌ Not Started)

### 4. GTFS Static — `api.data.gov.my/gtfs-static/<agency>`

Returns **ZIP files** containing GTFS feed data (routes, stops, schedules, etc.).

| Operator | Endpoint |
|----------|----------|
| KTMB | `/gtfs-static/ktmb` |
| Prasarana | `/gtfs-static/prasarana?category=<cat>` |
| BAS.MY (9 cities) | `/gtfs-static/mybas-<kangar|alor-setar|kota-bharu|kuala-terengganu|ipoh|seremban-a|seremban-b|melaka|johor|kuching>` |

**Prasarana categories:** `rapid-bus-penang`, `rapid-bus-kuantan`, `rapid-bus-mrtfeeder`, `rapid-rail-kl`, `rapid-bus-kl`

**Refresh:** Daily at 4am recommended.

### 5. GTFS Realtime — `api.data.gov.my/gtfs-realtime/<feed>/<agency>`

Returns **protobuf** (`.proto`) files with live vehicle positions.

| Feed Type | Endpoint Pattern |
|-----------|-----------------|
| Vehicle Position | `/gtfs-realtime/vehicle-position/<agency>` |
| Trip Updates | Planned for 2026 |
| Service Alerts | Planned for 2026 |

**Update frequency:** Every 30 seconds. **Same agencies** as GTFS Static.

---

## Summary

| API | Format | Implemented | Difficulty |
|-----|--------|-------------|-----------|
| OpenDOSM | JSON | ✅ Yes | — |
| Data Catalogue | JSON | ✅ Yes | — |
| Weather | JSON | ❌ No | 🟢 Easy |
| GTFS Static | ZIP | ❌ No | 🟡 Medium |
| GTFS Realtime | Protobuf | ❌ No | 🔴 Hard |
