"""Database layer: lazy SQLAlchemy 2.0 engine, session factory, declarative Base.

The engine is created on first use only — the API process must start and serve
/healthz and stub endpoints without a reachable PostgreSQL (docs/05 §7 demo
resilience). Nothing in this module connects at import time.
"""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

# Deterministic constraint names keep future Alembic diffs boring.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Declarative base for all IGERIM models (docs/05 §4)."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def normalize_database_url(url: str) -> str:
    """Managed Postgres providers (Render/Heroku/Railway) hand out a bare
    ``postgres://`` URL; SQLAlchemy 2.0 needs a driver — coerce it to
    ``postgresql+psycopg://`` so a copy-pasted connection string just works (H5)."""
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Create (once) and return the engine. Does not open a connection."""
    return create_engine(
        normalize_database_url(get_settings().database_url), pool_pre_ping=True
    )


@lru_cache(maxsize=1)
def get_sessionmaker() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yield a session, always close it."""
    session = get_sessionmaker()()
    try:
        yield session
    finally:
        session.close()
