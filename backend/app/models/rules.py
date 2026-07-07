"""Rule catalog mirror, findings and rule runs (docs/05 §4, docs/06 §7)."""

import datetime
import uuid
from typing import Any

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.enums import FindingStatus, RuleSeverity, text_enum


class Rule(Base):
    """DB mirror of rules/*.yaml — the YAML catalog stays the source of truth."""

    __tablename__ = "rules"

    code: Mapped[str] = mapped_column(String(8), primary_key=True)  # R01..R25
    severity: Mapped[RuleSeverity] = mapped_column(text_enum(RuleSeverity))
    scope: Mapped[str] = mapped_column(String(32))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    params: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    message_kk: Mapped[str] = mapped_column(Text)
    message_ru: Mapped[str] = mapped_column(Text)
    origin: Mapped[str] = mapped_column(String(64))


class RuleRun(Base):
    __tablename__ = "rule_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    scope: Mapped[str] = mapped_column(String(64))
    started_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    totals: Mapped[dict[str, Any] | None] = mapped_column(JSONB)


class Finding(Base):
    """Idempotent per (run, rule, claim) — enforced by the rules engine."""

    __tablename__ = "findings"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rule_runs.id"), index=True)
    rule_code: Mapped[str] = mapped_column(ForeignKey("rules.code"), index=True)
    claim_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("claims.id"), index=True)
    amount_at_risk: Mapped[int] = mapped_column(BigInteger, default=0)  # whole tenge
    details: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    status: Mapped[FindingStatus] = mapped_column(
        text_enum(FindingStatus), default=FindingStatus.open, index=True
    )
