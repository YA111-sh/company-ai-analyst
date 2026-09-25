import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@dataclass(frozen=True)
class Settings:
    mssql_server: str
    mssql_database: str
    mssql_user: str
    mssql_password: str
    foundry_project_endpoint: str
    foundry_model: str


settings = Settings(
    mssql_server=_require("MSSQL_SERVER"),
    mssql_database=_require("MSSQL_DATABASE"),
    mssql_user=_require("MSSQL_USER"),
    mssql_password=_require("MSSQL_PASSWORD"),
    foundry_project_endpoint = _require("PROJECT_ENDPOINT"),
    foundry_model = _require("MODEL_NAME")
)