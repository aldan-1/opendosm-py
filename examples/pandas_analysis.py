"""Pandas analysis example — convert API data to DataFrames."""

from opendosm import OpenDOSM, QueryBuilder

client = OpenDOSM()

# Fetch CPI data and convert to DataFrame
query = QueryBuilder().limit(100)
data = client.opendosm.cpi(query=query)
df = client.to_dataframe(data)

print("=== CPI DataFrame ===")
print(df.head(10))
print(f"\nShape: {df.shape}")
print(f"\nData types:\n{df.dtypes}")

# Basic analysis
if "value" in df.columns:
    print(f"\nMean CPI value: {df['value'].mean():.2f}")
    print(f"Min CPI value:  {df['value'].min():.2f}")
    print(f"Max CPI value:  {df['value'].max():.2f}")

client.close()
