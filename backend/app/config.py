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

    # Auth / session (EPIC G1). Demo defaults — override via env in prod. The
    # cookie is a signed, timestamped payload (itsdangerous), no server store.
    secret_key: str = "qalam-demo-secret-change-in-prod-0a1b2c3d4e5f"
    session_cookie: str = "qalam_session"
    session_max_age: int = 86_400  # 24h
    # Header token that lets headless scripts (scripts/qa_golden.py, CI) act as
    # an admin service principal without a login round-trip.
    service_token: str = "qalam-service-token-demo"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
