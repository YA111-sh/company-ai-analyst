import urllib.parse
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from src.ai.config import settings
from sqlalchemy import text



@lru_cache(maxsize=1)
def get_engine() -> Engine:
    password = settings.mssql_password.replace("}", "}}")
    odbc = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={settings.mssql_server};"
        f"DATABASE={settings.mssql_database};"
        f"UID={settings.mssql_user};"
        f"PWD={{{password}}};"
        "Encrypt=yes;TrustServerCertificate=yes;"
    )
    url = "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(odbc)
    return create_engine(url, pool_pre_ping=True)




def check_db() -> dict:
    with get_engine().connect() as conn:
        db = conn.execute(text("SELECT DB_NAME()")).scalar()
        version = conn.execute(text("SELECT @@VERSION")).scalar()
    return {"database": db, "version": version.splitlines()[0]}


if __name__ == "__main__":
    print(check_db())