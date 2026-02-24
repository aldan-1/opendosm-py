"""Test the 'datasets' meta-dataset for dynamic discovery.
Validate the approach before implementing list_datasets() and search()."""

from opendosm import OpenDOSM

client = OpenDOSM()

# ── 1. Fetch all datasets ──────────────────────────────────────────
print("=== 1. Fetch All Datasets ===")
all_ds = client.data_catalogue.get("datasets")
print(f"Total datasets: {len(all_ds)}")
print(f"Record keys: {list(all_ds[0].keys())}")
print()

# ── 2. List all categories ─────────────────────────────────────────
print("=== 2. Available Categories ===")
categories = sorted(set(d["category_en"] for d in all_ds))
for cat in categories:
    count = sum(1 for d in all_ds if d["category_en"] == cat)
    print(f"  {cat:30s} ({count} datasets)")
print()

# ── 3. Filter by category ──────────────────────────────────────────
print("=== 3. Filter by Category (Demography) ===")
demo = [d for d in all_ds if d["category_en"] == "Demography"]
for d in demo[:5]:
    print(f"  {d['id']:40s} {d['title_en']}")
if len(demo) > 5:
    print(f"  ... and {len(demo) - 5} more")
print()

# ── 4. Search by title/id ──────────────────────────────────────────
print("=== 4. Search for 'fuel' ===")
fuel = [d for d in all_ds if "fuel" in d["id"].lower() or "fuel" in d["title_en"].lower()]
for d in fuel:
    print(f"  {d['id']:40s} {d['title_en']}")
print()

print("=== 5. Search for 'gdp' ===")
gdp = [d for d in all_ds if "gdp" in d["id"].lower() or "gdp" in d["title_en"].lower()]
for d in gdp:
    print(f"  {d['id']:40s} {d['title_en']}")
print()

print("=== 6. Search for 'trade' ===")
trade = [d for d in all_ds if "trade" in d["id"].lower() or "trade" in d["title_en"].lower()]
for d in trade:
    print(f"  {d['id']:40s} {d['title_en']}")
print()

# ── 7. Verify some discovered IDs actually work ────────────────────
print("=== 7. Verify Discovered IDs Work ===")
test_ids = [d["id"] for d in gdp[:3]] + [d["id"] for d in trade[:3]]
for dataset_id in test_ids:
    try:
        data = client.data_catalogue.get(dataset_id, limit=1)
        print(f"  OK   {dataset_id}")
    except Exception as e:
        print(f"  FAIL {dataset_id} -> {type(e).__name__}")
print()

# ── 8. Check available sources ─────────────────────────────────────
print("=== 8. Data Sources ===")
sources = sorted(set(d["source"] for d in all_ds))
for s in sources[:15]:
    count = sum(1 for d in all_ds if d["source"] == s)
    print(f"  {s:30s} ({count} datasets)")
if len(sources) > 15:
    print(f"  ... and {len(sources) - 15} more")
print()

# ── 9. Check frequencies ──────────────────────────────────────────
print("=== 9. Update Frequencies ===")
freqs = sorted(set(d["frequency"] for d in all_ds))
for f in freqs:
    count = sum(1 for d in all_ds if d["frequency"] == f)
    print(f"  {f:20s} ({count} datasets)")

client.close()
print()
print("All discovery tests complete!")
