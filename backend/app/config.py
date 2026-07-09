"""Application settings loaded from environment variables (pydantic-settings)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DATABASE_URL = "postgresql+psycopg://igerim:igerim@localhost:55432/igerim"


class Settings(BaseSettings):
    """Runtime configuration; every field overridable via environment."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = DEFAULT_DATABASE_URL
    cors_origins: list[str] = ["http://localhost:3000"]
    app_name: str = "IGERIM API"
    api_v1_prefix: str = "/api/v1"

    # Комплексный подушевой норматив (КПН/ПН), ₸/чел/мес — the base the ЕКД
    # АПП penalties are counted in («100 КПН» etc.). gp14-real ≈ 1710
    # (calibration_stats.md). Used to money-ize the sanction-risk verdict.
    kpn_tenge: int = 1710


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
