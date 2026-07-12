"""Unit tests for the cloud-deploy config coercions (EPIC H5 / Render).

No database: these guard two things that silently broke a real Render deploy —
(1) the bare ``postgres://`` URL that managed Postgres hands out must be coerced
to a SQLAlchemy-2.0 driver (used by both app/db.py and migrations/env.py, else
alembic raises NoSuchModuleError and the schema is never created), and (2) a
CORS origin pasted with a path (``https://app/login``) must be normalized to a
bare origin or it never matches the browser's Origin header.
"""

import pytest

from app.config import Settings
from app.db import normalize_database_url


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        # Render/Heroku/Railway hand out a bare postgres:// — SQLAlchemy 2.0
        # dropped that dialect alias, so it MUST be coerced.
        ("postgres://u:p@host:5432/db", "postgresql+psycopg://u:p@host:5432/db"),
        ("postgresql://u:p@host:5432/db", "postgresql+psycopg://u:p@host:5432/db"),
        # Already-qualified URLs pass through untouched.
        (
            "postgresql+psycopg://u:p@host:5432/db",
            "postgresql+psycopg://u:p@host:5432/db",
        ),
    ],
)
def test_normalize_database_url(raw: str, expected: str) -> None:
    assert normalize_database_url(raw) == expected


def test_cors_origins_strips_path_and_trailing_slash() -> None:
    # A full URL with a path (the classic mistake) must collapse to the origin.
    s = Settings(cors_origins="https://alemai-mu.vercel.app/login")
    assert s.cors_origins_list == ["https://alemai-mu.vercel.app"]


def test_cors_origins_multi_and_port_preserved() -> None:
    s = Settings(
        cors_origins="http://localhost:3000, https://app.vercel.app/, https://x.io/a/b"
    )
    assert s.cors_origins_list == [
        "http://localhost:3000",
        "https://app.vercel.app",
        "https://x.io",
    ]


def test_cors_origins_empty_entries_dropped() -> None:
    s = Settings(cors_origins="https://a.com,, ,https://b.com")
    assert s.cors_origins_list == ["https://a.com", "https://b.com"]


def test_cookie_defaults_are_local_safe() -> None:
    # Local default is the same-site Lax/insecure cookie; cloud overrides via env.
    s = Settings()
    assert s.cookie_samesite == "lax"
    assert s.cookie_secure is False


def test_cookie_env_overrides_apply() -> None:
    s = Settings(cookie_samesite="none", cookie_secure=True)
    assert s.cookie_samesite == "none"
    assert s.cookie_secure is True
