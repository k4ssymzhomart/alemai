"""Application settings loaded from environment variables (pydantic-settings)."""

from functools import lru_cache
from urllib.parse import urlsplit

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DATABASE_URL = "postgresql+psycopg://igerim:igerim@localhost:55432/igerim"


class Settings(BaseSettings):
    """Runtime configuration; every field overridable via environment."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = DEFAULT_DATABASE_URL
    # Comma-separated so a deploy can set CORS_ORIGINS="https://a,https://b" as a
    # plain env string (pydantic-settings would JSON-parse a list field). H5.
    cors_origins: str = "http://localhost:3000"
    app_name: str = "IGERIM API"
    api_v1_prefix: str = "/api/v1"

    # Комплексный подушевой норматив (КПН/ПН), ₸/чел/мес — the base the ЕКД
    # АПП penalties are counted in («100 КПН» etc.). gp14-real ≈ 1710
    # (calibration_stats.md). Used to money-ize the sanction-risk verdict.
    kpn_tenge: int = 1710
    # МРП (месячный расчётный показатель), ₸ — 2026 = 4 325 (закон №239-VIII от
    # 08.12.2025). The 200/800-МРП reputational thresholds derive from it. H0.
    mrp_tenge: int = 4325

    # Auth / session (EPIC G1). Demo defaults — override via env in prod. The
    # cookie is a signed, timestamped payload (itsdangerous), no server store.
    secret_key: str = "qalam-demo-secret-change-in-prod-0a1b2c3d4e5f"
    session_cookie: str = "qalam_session"
    session_max_age: int = 86_400  # 24h
    # Cross-site deploys (frontend on Vercel, API on Render are different sites)
    # require SameSite=None + Secure or the browser won't store/send the session
    # cookie on API calls. Local same-site HTTP keeps the Lax/insecure defaults.
    # Cloud sets COOKIE_SAMESITE=none + COOKIE_SECURE=true (see render.yaml). H5.
    # NB: Safari/ITP blocks third-party cookies outright — cross-site cookie auth
    # works on Chromium/Firefox; a token/header scheme would be needed for Safari.
    cookie_samesite: str = "lax"
    cookie_secure: bool = False
    # Header token that lets headless scripts (scripts/qa_golden.py, CI) act as
    # an admin service principal without a login round-trip.
    service_token: str = "qalam-service-token-demo"

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS allow-list from the comma-separated ``cors_origins``, each
        normalized to ``scheme://host[:port]``. A pasted full URL with a path
        (e.g. ``https://app.vercel.app/login``) or a trailing slash would never
        match the browser's ``Origin`` header (always bare scheme+host), so we
        strip everything past the authority. H5."""
        origins: list[str] = []
        for raw in self.cors_origins.split(","):
            raw = raw.strip()
            if not raw:
                continue
            parts = urlsplit(raw)
            if parts.scheme and parts.netloc:
                origins.append(f"{parts.scheme}://{parts.netloc}")
            else:
                origins.append(raw.rstrip("/"))
        return origins


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
