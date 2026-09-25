import pandas as pd
from sqlalchemy import text
from src.ai.db.connection import get_engine

df = pd.read_sql(
    text("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES ORDER BY 1, 2"),
    get_engine(),
)
print(df.to_string())