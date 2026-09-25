import pandas as pd
from sqlalchemy import text
from src.ai.db.connection import get_engine

df = pd.read_sql(
    text("""
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'Company'
        ORDER BY ORDINAL_POSITION
    """),
    get_engine(),
)
print(df.to_string())