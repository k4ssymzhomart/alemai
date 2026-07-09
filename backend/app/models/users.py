"""Users (4 hardcoded demo roles) and audit log (docs/05 §4, docs/04 §1)."""

import datetime
import uuid

from sqlalchemy import DateTime, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.enums import UserRole, text_enum


def _utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(128))
    role: Mapped[UserRole] = mapped_column(text_enum(UserRole))
    # Login identity + PBKDF2 hash (EPIC G1). nullable in DB for the pre-G1
    # schema; every seeded user sets both.
    username: Mapped[str | None] = mapped_column(String(64), unique=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    # Per-user notifications read cursor (G3): unread = events after this ts.
    notifications_read_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True)
    )


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    who: Mapped[str] = mapped_column(String(128))  # user id or role name
    what: Mapped[str] = mapped_column(Text)
    when: Mapped[datetime.datetime] = mapped_column(
        "when", DateTime(timezone=True), default=_utcnow
    )
