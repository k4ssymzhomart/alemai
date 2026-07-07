"""Alerts and deadline calendar (docs/05 §4, F1)."""

import datetime
import uuid

from sqlalchemy import BigInteger, Date, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.enums import AlertSeverity, AlertStatus, DeadlineKind, text_enum


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String(64))
    severity: Mapped[AlertSeverity] = mapped_column(text_enum(AlertSeverity))
    title_kk: Mapped[str] = mapped_column(String(255))
    title_ru: Mapped[str] = mapped_column(String(255))
    amount: Mapped[int | None] = mapped_column(BigInteger)  # whole tenge
    due_date: Mapped[datetime.date | None] = mapped_column(Date)
    entity_ref: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[AlertStatus] = mapped_column(
        text_enum(AlertStatus), default=AlertStatus.active, index=True
    )


class Deadline(Base):
    """Seeded config; exact dates must be verified onsite (docs/05 §4 warning)."""

    __tablename__ = "deadlines"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    kind: Mapped[DeadlineKind] = mapped_column(text_enum(DeadlineKind))
    starts: Mapped[datetime.date] = mapped_column(Date)
    ends: Mapped[datetime.date] = mapped_column(Date)
    note: Mapped[str | None] = mapped_column(Text)
