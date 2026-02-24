"""Live API tests 1-10 for the OpenDOSM SDK."""

from opendosm import OpenDOSM
from opendosm.query import QueryBuilder
from opendosm.exceptions import NotFoundError
from opendosm.models import APIResponse

client = OpenDOSM()

# ── Test 1: Basic fetch ────────────────────────────────────────────
print("=== TEST 1: Basic Fetch ===")
data = client.opendosm.get("cpi_core", limit=5)
print(f"Got {len(data)} records")
print(f"First record: {data[0]}")
print()

# ── Test 2: Convenience methods ────────────────────────────────────
print("=== TEST 2: Convenience Methods ===")
cpi = client.opendosm.cpi(limit=3)
print(f"CPI:        {len(cpi)} records  -> keys: {list(cpi[0].keys())}")

gdp = client.opendosm.gdp(limit=3)
print(f"GDP:        {len(gdp)} records  -> keys: {list(gdp[0].keys())}")

pop = client.opendosm.population(limit=3)
print(f"Population: {len(pop)} records  -> keys: {list(pop[0].keys())}")

trade = client.opendosm.trade(limit=3)
print(f"Trade:      {len(trade)} records  -> keys: {list(trade[0].keys())}")

labour = client.opendosm.labour(limit=3)
print(f"Labour:     {len(labour)} records  -> keys: {list(labour[0].keys())}")
print()

# ── Test 3: Filtering by state ─────────────────────────────────────
print("=== TEST 3: QueryBuilder - Filtering ===")
q = QueryBuilder().filter(state="Selangor").limit(10)
data = client.opendosm.population(query=q)
print(f"Selangor records: {len(data)}")
for r in data[:3]:
    print(f"  state={r.get('state')}, date={r.get('date')}, pop={r.get('population')}")
print()

# ── Test 4: Sorting + column selection ─────────────────────────────
print("=== TEST 4: QueryBuilder - Sort + Include ===")
q = QueryBuilder().sort("date", descending=True).limit(5).include("date", "index")
data = client.opendosm.cpi(query=q)
for r in data:
    print(f"  {r}")
keys_ok = all(set(r.keys()) == {"date", "index"} for r in data)
print(f"  Only 'date' & 'index' keys? {keys_ok}")
print()

# ── Test 5: Date range ─────────────────────────────────────────────
print("=== TEST 5: QueryBuilder - Date Range ===")
q = QueryBuilder().date_range("date", start="2023-01-01", end="2023-12-31").limit(10)
data = client.opendosm.cpi(query=q)
print(f"CPI records in 2023: {len(data)}")
for r in data[:3]:
    print(f"  date={r.get('date')}, index={r.get('index')}")
print()

# ── Test 6: Metadata response ─────────────────────────────────────
print("=== TEST 6: Metadata Response ===")
data = client.opendosm.get("cpi_core", meta=True, limit=5)
print(f"  Type: {type(data).__name__}")
is_api_response = isinstance(data, APIResponse)
print(f"  Is APIResponse? {is_api_response}")
if is_api_response:
    print(f"  Meta: {data.meta}")
    print(f"  Data count: {len(data.data)}")
print()

# ── Test 7: Data Catalogue API ─────────────────────────────────────
print("=== TEST 7: Data Catalogue API ===")
cat_data = client.data_catalogue.get("fuelprice", limit=5)
print(f"Fuel price records: {len(cat_data)}")
print(f"First record: {cat_data[0]}")
print()

# ── Test 8: Pandas integration ─────────────────────────────────────
print("=== TEST 8: Pandas Integration ===")
try:
    raw = client.opendosm.cpi(limit=20)
    df = client.to_dataframe(raw)
    print(f"  DataFrame shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Dtypes:")
    print(df.dtypes.to_string())
    print(f"  Head:")
    print(df.head(3).to_string())
except ImportError as e:
    print(f"  SKIP (pandas not installed): {e}")
print()

# ── Test 9: Context manager ───────────────────────────────────────
print("=== TEST 9: Context Manager ===")
with OpenDOSM() as ctx_client:
    data = ctx_client.opendosm.trade(limit=5)
    print(f"  Trade records: {len(data)}")
print("  Client closed automatically - OK")
print()

# ── Test 10: Error handling ────────────────────────────────────────
print("=== TEST 10: Error Handling ===")
try:
    client.opendosm.get("nonexistent_dataset_xyz_123")
    print("  FAIL - no error raised!")
except NotFoundError as e:
    print(f"  Caught expected NotFoundError: {e}")
except Exception as e:
    print(f"  Caught unexpected {type(e).__name__}: {e}")

client.close()

print()
print("=" * 50)
print("All 10 tests complete!")
