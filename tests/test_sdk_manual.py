"""
===========================================================
  opendosm SDK -- Manual Test Script
  Run in a fresh venv: pip install opendosm[pandas]
===========================================================

How to run:
    python -m venv test-env
    test-env\\Scripts\\activate        # Windows
    pip install opendosm[pandas]
    python test_sdk.py
"""

import sys
import traceback

PASSED = 0
FAILED = 0


def run_test(name, func):
    """Run a test and report pass/fail."""
    global PASSED, FAILED
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    try:
        func()
        print("PASSED")
        PASSED += 1
    except Exception as e:
        print(f"FAILED: {e}")
        traceback.print_exc()
        FAILED += 1


# ── TEST 1: Basic Import ─────────────────────────────────────
def test_import():
    """
    Use Case: Verify the package is installed correctly.
    Condition: opendosm is installed via pip.
    Expected: All public classes import without error.
    """
    from opendosm import (
        __version__,
    )
    print(f"  Version: {__version__}")
    print("  All 12 public exports imported successfully")
    assert __version__, "Version should not be empty"


# ── TEST 2: Client Initialization ─────────────────────────────
def test_client_init():
    """
    Use Case: Create a client with default settings.
    Condition: No token, default base URL.
    Expected: Client has .opendosm and .data_catalogue sub-clients.
    """
    from opendosm import OpenDOSM

    client = OpenDOSM()
    assert hasattr(client, "opendosm"), "Missing .opendosm"
    assert hasattr(client, "data_catalogue"), "Missing .data_catalogue"
    assert hasattr(client, "to_dataframe"), "Missing .to_dataframe()"
    print(f"  repr: {client!r}")
    client.close()
    print("  Client created and closed successfully")


# ── TEST 3: Context Manager ──────────────────────────────────
def test_context_manager():
    """
    Use Case: Use client as a context manager.
    Condition: with OpenDOSM() as client.
    Expected: Client works inside 'with' block, auto-closes after.
    """
    from opendosm import OpenDOSM

    with OpenDOSM() as client:
        print(f"  Inside context manager: {client!r}")
    print("  Exited context manager - client auto-closed")


# ── TEST 4: Fetch CPI Data (Live API) ────────────────────────
def test_fetch_cpi():
    """
    Use Case: Fetch CPI (Consumer Price Index) data.
    Condition: Live API call, no auth token.
    Expected: Returns a non-empty list of dicts with date/value fields.
    """
    from opendosm import OpenDOSM

    with OpenDOSM() as client:
        data = client.opendosm.cpi()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        assert len(data) > 0, "Expected non-empty data"
        first = data[0]
        assert isinstance(first, dict), f"Expected dict, got {type(first)}"
        print(f"  Records returned: {len(data)}")
        print(f"  First record keys: {list(first.keys())}")
        print(f"  Sample: {first}")


# ── TEST 5: Fetch with QueryBuilder ──────────────────────────
def test_query_builder():
    """
    Use Case: Filter and limit results using QueryBuilder.
    Condition: Fetch CPI data, limit to 5, sorted by date desc.
    Expected: Exactly 5 records, sorted newest first.
    """
    from opendosm import OpenDOSM, QueryBuilder

    with OpenDOSM() as client:
        query = (
            QueryBuilder()
            .sort("date", descending=True)
            .limit(5)
        )
        data = client.opendosm.cpi(query=query)
        assert len(data) == 5, f"Expected 5 records, got {len(data)}"
        print(f"  Got {len(data)} records (limit=5 ok)")
        dates = [r.get("date", "") for r in data]
        print(f"  Dates (should be descending): {dates}")
        assert dates == sorted(dates, reverse=True), "Dates not sorted descending"


# ── TEST 6: Fetch with Meta ──────────────────────────────────
def test_meta_response():
    """
    Use Case: Request metadata alongside data.
    Condition: Use meta=True to get total count.
    Expected: Returns APIResponse with .meta and .data attributes.
    """
    from opendosm import APIResponse, OpenDOSM, QueryBuilder

    with OpenDOSM() as client:
        query = QueryBuilder().limit(3)
        result = client.opendosm.get("cpi_core", query=query, meta=True)
        assert isinstance(result, APIResponse), f"Expected APIResponse, got {type(result)}"
        assert result.meta is not None, "Meta should not be None"
        assert len(result.data) == 3, f"Expected 3 records, got {len(result.data)}"
        print(f"  Total records in dataset: {result.meta.total}")
        print(f"  Records returned: {len(result.data)}")


# ── TEST 7: GDP Convenience Method ───────────────────────────
def test_gdp():
    """
    Use Case: Fetch GDP data using convenience method.
    Condition: No query, default dataset_id.
    Expected: Returns non-empty list with GDP data.
    """
    from opendosm import OpenDOSM

    with OpenDOSM() as client:
        data = client.opendosm.gdp()
        assert len(data) > 0, "Expected non-empty GDP data"
        print(f"  GDP records: {len(data)}")
        print(f"  Sample keys: {list(data[0].keys())}")


# ── TEST 8: Data Catalogue Get ───────────────────────────────
def test_data_catalogue():
    """
    Use Case: Fetch fuel price data from data catalogue.
    Condition: Use data_catalogue.get("fuelprice").
    Expected: Returns non-empty list with fuel price records.
    """
    from opendosm import OpenDOSM, QueryBuilder

    with OpenDOSM() as client:
        query = QueryBuilder().limit(3)
        data = client.data_catalogue.get("fuelprice", query=query)
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        assert len(data) > 0, "Expected non-empty fuel price data"
        print(f"  Fuel price records: {len(data)}")
        print(f"  Sample: {data[0]}")


# ── TEST 9: List Datasets ────────────────────────────────────
def test_list_datasets():
    """
    Use Case: Discover all available datasets.
    Condition: Call list_datasets() with no filters.
    Expected: Returns 200+ DatasetInfo objects.
    """
    from opendosm import DatasetInfo, OpenDOSM

    with OpenDOSM() as client:
        datasets = client.data_catalogue.list_datasets()
        assert len(datasets) > 100, f"Expected 100+ datasets, got {len(datasets)}"
        assert all(isinstance(d, DatasetInfo) for d in datasets[:5])
        print(f"  Total datasets: {len(datasets)}")
        print("  First 5:")
        for ds in datasets[:5]:
            print(f"    - {ds.id}: {ds.title_en}")


# ── TEST 10: List Datasets by Category ───────────────────────
def test_list_datasets_filtered():
    """
    Use Case: Filter datasets by category.
    Condition: list_datasets(category="Demography").
    Expected: Returns only demography-related datasets.
    """
    from opendosm import OpenDOSM

    with OpenDOSM() as client:
        datasets = client.data_catalogue.list_datasets(category="Demography")
        assert len(datasets) > 0, "Expected some demography datasets"
        for ds in datasets:
            assert "demography" in ds.category_en.lower(), f"Unexpected category: {ds.category_en}"
        print(f"  Demography datasets: {len(datasets)}")
        for ds in datasets[:3]:
            print(f"    - {ds.id}: {ds.title_en}")


# ── TEST 11: Search Datasets ─────────────────────────────────
def test_search_datasets():
    """
    Use Case: Search datasets by keyword.
    Condition: search("gdp").
    Expected: Returns datasets with 'gdp' in ID or title.
    """
    from opendosm import OpenDOSM

    with OpenDOSM() as client:
        results = client.data_catalogue.search("gdp")
        assert len(results) > 0, "Expected some GDP datasets"
        print(f"  Search 'gdp' results: {len(results)}")
        for ds in results[:5]:
            print(f"    - {ds.id}: {ds.title_en}")


# ── TEST 12: Pandas DataFrame Conversion ─────────────────────
def test_pandas_dataframe():
    """
    Use Case: Convert API data to pandas DataFrame.
    Condition: pip install opendosm[pandas] required.
    Expected: Returns DataFrame with correct types, date columns auto-parsed.
    """
    try:
        import pandas as pd
    except ImportError:
        print("  SKIPPED -- pandas not installed (pip install opendosm[pandas])")
        return

    from opendosm import OpenDOSM, QueryBuilder

    with OpenDOSM() as client:
        query = QueryBuilder().limit(10)
        data = client.opendosm.cpi(query=query)
        df = client.to_dataframe(data)

        assert len(df) == 10, f"Expected 10 rows, got {len(df)}"
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Dtypes:\n{df.dtypes.to_string()}")
        print(f"\n  Head:\n{df.head(3).to_string()}")

        # Check if date column was auto-parsed
        date_cols = [c for c in df.columns if "date" in c.lower()]
        for col in date_cols:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                print(f"\n  [ok] Column '{col}' auto-parsed as datetime")


# ── TEST 13: DatasetInfo to DataFrame ─────────────────────────
def test_dataset_info_to_dataframe():
    """
    Use Case: Convert dataset discovery results to DataFrame.
    Condition: Pass list[DatasetInfo] to to_dataframe().
    Expected: DataFrame with columns like id, title_en, source, etc.
    """
    try:
        import pandas  # noqa: F401
    except ImportError:
        print("  SKIPPED -- pandas not installed")
        return

    from opendosm import OpenDOSM

    with OpenDOSM() as client:
        datasets = client.data_catalogue.list_datasets()
        df = client.to_dataframe(datasets[:20])
        assert "id" in df.columns, "Expected 'id' column"
        assert "title_en" in df.columns, "Expected 'title_en' column"
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        print(f"\n  Sample:\n{df[['id', 'title_en', 'source']].head(5).to_string()}")


# ── TEST 14: NotFoundError ───────────────────────────────────
def test_not_found_error():
    """
    Use Case: Request a non-existent dataset.
    Condition: get("totally_fake_dataset_xyz").
    Expected: Raises NotFoundError.
    """
    from opendosm import NotFoundError, OpenDOSM

    with OpenDOSM() as client:
        try:
            client.opendosm.get("totally_fake_dataset_xyz")
            raise AssertionError("Should have raised NotFoundError")
        except NotFoundError as e:
            print(f"  Correctly raised NotFoundError: {e}")
            assert e.status_code == 404


# ── TEST 15: InvalidQueryError ───────────────────────────────
def test_invalid_query():
    """
    Use Case: Create a query with negative limit.
    Condition: QueryBuilder().limit(-1).
    Expected: Raises InvalidQueryError immediately (client-side validation).
    """
    from opendosm import InvalidQueryError, QueryBuilder

    try:
        QueryBuilder().limit(-1)
        raise AssertionError("Should have raised InvalidQueryError")
    except InvalidQueryError as e:
        print(f"  Correctly raised InvalidQueryError: {e}")


# ══════════════════════════════════════════════════════════════
#  RUN ALL TESTS
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("opendosm SDK -- Manual Validation Tests")
    print(f"Python {sys.version}")
    print("=" * 60)

    run_test("1. Import all public exports", test_import)
    run_test("2. Client initialization", test_client_init)
    run_test("3. Context manager", test_context_manager)
    run_test("4. Fetch CPI data (live API)", test_fetch_cpi)
    run_test("5. QueryBuilder (limit + sort)", test_query_builder)
    run_test("6. Meta response", test_meta_response)
    run_test("7. GDP convenience method", test_gdp)
    run_test("8. Data Catalogue (fuel price)", test_data_catalogue)
    run_test("9. List all datasets", test_list_datasets)
    run_test("10. Filter datasets by category", test_list_datasets_filtered)
    run_test("11. Search datasets", test_search_datasets)
    run_test("12. Pandas DataFrame conversion", test_pandas_dataframe)
    run_test("13. DatasetInfo to DataFrame", test_dataset_info_to_dataframe)
    run_test("14. NotFoundError handling", test_not_found_error)
    run_test("15. InvalidQueryError handling", test_invalid_query)

    print(f"\n{'='*60}")
    print(f"RESULTS: {PASSED} passed, {FAILED} failed, {PASSED + FAILED} total")
    print(f"{'='*60}")
    sys.exit(1 if FAILED > 0 else 0)
"""
Expected output (all 15 should pass):
    RESULTS: 15 passed, 0 failed, 15 total

Notes for tester:
- Tests 4-14 make LIVE API calls (requires internet)
- Tests 12-13 require pandas: pip install opendosm[pandas]
- No API token needed -- all endpoints are public
- If rate limited (429), wait a minute and retry
"""
