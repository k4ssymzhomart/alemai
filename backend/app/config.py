"""Application settings loaded from environment variables (pydantic-settings)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DATABASE_URL = "postgresql+psycopg://igerim:igerim@localhost:5432/igerim"


class Settings(BaseSettings):
    """Runtime configuration; every field overridable via environment."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = DEFAULT_DATABASE_URL
    cors_origins: list[str] = ["http://localhost:3000"]
    app_name: str = "IGERIM API"
    api_v1_prefix: str = "/api/v1"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
