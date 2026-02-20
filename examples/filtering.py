"""Filtering example — showcasing the QueryBuilder."""

from opendosm import OpenDOSM, QueryBuilder

client = OpenDOSM()

# Build a query with multiple filters
query = (
    QueryBuilder()
    .filter(state="Selangor")
    .date_range("date", start="2023-01-01", end="2023-12-31")
    .sort("date", descending=True)
    .limit(20)
    .include("date", "state", "value")
)

print(f"Query params: {query.build()}")
print()

# Use the query with an API call
data = client.opendosm.get("cpi_core", query=query)
print("=== CPI Core — Selangor, 2023 (sorted desc) ===")
for record in data:
    print(record)

client.close()
