import pandas as pd
from sqlalchemy import text
from src.ai.db.connection import get_engine

df = pd.read_sql(text("SELECT TOP (50000) * FROM dbo.Company"), get_engine())

print("Rows loaded:", len(df))
print()

profile = pd.DataFrame({
    "dtype": df.dtypes.astype(str),
    "null_%": (df.isna().mean() * 100).round(1),
    "distinct": df.nunique(),
})
print(profile.to_string())
print()

for col in df.columns:
    if df[col].dtype == "object" and df[col].nunique() <= 30:
        print(f"--- {col} ---")
        print(df[col].value_counts(dropna=False).head(10).to_string())
        print()

for col in df.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns:
    print(f"{col}: {df[col].min()} to {df[col].max()}")