"""Domain events + lightweight app config (EPIC G2/G4).

``events`` is the append-only feed that powers realtime-across-sessions: every
meaningful mutation writes one row, and clients poll ``GET /events`` to refresh
their caches and surface notifications. ``app_config`` is a tiny key→JSON store
for thresholds and demo-reset bookkeeping (no dedicated settings tables).
"""

import datetime
import uuid
from typing import Any

from sqlalchemy import DateTime, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def _utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ts: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, index=True
    )
    type: Mapped[str] = mapped_column(String(48), index=True)
    severity: Mapped[str] = mapped_column(String(16), default="info")  # info|warn|critical
    actor: Mapped[str] = mapped_column(String(128), default="Жүйе")
    actor_username: Mapped[str | None] = mapped_column(String(64))
    role: Mapped[str | None] = mapped_column(String(32))
    entity_ref: Mapped[str | None] = mapped_column(String(160))
    link: Mapped[str | None] = mapped_column(String(255))  # frontend route to the entity
    title_kk: Mapped[str] = mapped_column(Text)
    title_ru: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB)


class AppConfig(Base):
    __tablename__ = "app_config"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[dict[str, Any]] = mapped_column(JSONB)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


class RadarCheck(Base):
    """Latest normative-source check per source (EPIC G5). One row per source,
    upserted on «Тексеру»."""

    __tablename__ = "radar_checks"

    source_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    checked_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    status: Mapped[str] = mapped_column(String(16))  # ok | stale | unreachable | manual
    our_version: Mapped[str | None] = mapped_column(String(64))
    detected_version: Mapped[str | None] = mapped_column(String(64))
    message: Mapped[str | None] = mapped_column(Text)


class ShareLink(Base):
    """Shareable state link (EPIC H3) — a short code → the exact route+state a
    user was looking at. Opening /s/<code> restores it (through the opener's own
    permissions). No external SaaS; this is the offline-safe collaboration."""

    __tablename__ = "share_links"

    code: Mapped[str] = mapped_column(String(16), primary_key=True)
    url_state: Mapped[dict[str, Any]] = mapped_column(JSONB)  # {path, query, locale}
    created_by: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    expires_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))


class DocumentVersion(Base):
    """Every docgen call persisted (EPIC H4) — params + deterministic auto-title
    so a доп.обращение can be re-run «с теми же параметрами»."""

    __tablename__ = "document_versions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    doc_type: Mapped[str] = mapped_column(String(32), index=True)
    entity_ref: Mapped[str | None] = mapped_column(String(160), index=True)
    params: Mapped[dict[str, Any]] = mapped_column(JSONB)
    author: Mapped[str | None] = mapped_column(String(64))
    author_name: Mapped[str | None] = mapped_column(String(128))
    ts: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, index=True
    )
    auto_title: Mapped[str] = mapped_column(Text)
    lang: Mapped[str] = mapped_column(String(4), default="ru")


class Comment(Base):
    """Notes + source suggestions threaded on radar rows / findings (EPIC H4)."""

    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    entity_ref: Mapped[str] = mapped_column(String(160), index=True)
    author: Mapped[str | None] = mapped_column(String(64))
    author_name: Mapped[str | None] = mapped_column(String(128))
    text: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(24), default="note")  # note|source_suggestion
    url: Mapped[str | None] = mapped_column(String(500))
    ts: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, index=True
    )
