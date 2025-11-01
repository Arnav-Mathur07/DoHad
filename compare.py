import pandas as pd

# Load both files
df_and = pd.read_csv("developmental and prenatal and arsenic.csv")
df_or = pd.read_csv("developmental or prenatal and arsenic.csv")

# Convert PubMed IDs to string (for consistency) and make sets
ids_and = set(df_and["PMID"].astype(str))
ids_or = set(df_or["PMID"].astype(str))

# Find unique IDs
unique_and = ids_and - ids_or   # in AND but not in OR
unique_or = ids_or - ids_and    # in OR but not in AND

# Filter the dataframes to keep only unique rows
df_unique_and = df_and[df_and["PMID"].astype(str).isin(unique_and)]
df_unique_or = df_or[df_or["PMID"].astype(str).isin(unique_or)]

# Save results
df_unique_and.to_csv("unique_prenatal_AND.csv", index=False)
df_unique_or.to_csv("unique_prenatal_OR.csv", index=False)

print("Unique AND results saved to unique_prenatal_AND.csv")
print("Unique OR results saved to unique_prenatal_OR.csv")
