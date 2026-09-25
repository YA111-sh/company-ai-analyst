from sqlalchemy import text
from src.ai.db.connection import get_engine

TABLE = "dbo.Company"


def fetch_rows(sql: str, params: dict | None = None, max_rows: int = 200) -> list[dict]:
    with get_engine().connect() as conn:
        result = conn.execute(text(sql), params or {})
        return [dict(r._mapping) for r in result.fetchmany(max_rows)]


def fetch_scalar(sql: str, params: dict | None = None):
    with get_engine().connect() as conn:
        return conn.execute(text(sql), params or {}).scalar()