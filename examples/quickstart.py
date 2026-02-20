"""Quickstart example — basic usage of the OpenDOSM SDK."""

from opendosm import OpenDOSM

# Create a client (no token needed for basic access)
client = OpenDOSM()

# Fetch the first 5 CPI records
cpi_data = client.opendosm.cpi()
print("=== CPI Core (first 5 records) ===")
for record in cpi_data[:5]:
    print(record)

# Fetch population data
population_data = client.opendosm.population()
print("\n=== Population by State (first 5 records) ===")
for record in population_data[:5]:
    print(record)

# Use with metadata
response = client.opendosm.get("cpi_core", meta=True)
print(f"\nMetadata: {response.meta}")
print(f"First record: {response.data[0] if response.data else 'None'}")

# Clean up
client.close()
