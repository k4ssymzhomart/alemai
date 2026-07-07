"""Forecasts and risk assessments (docs/05 §4, methodology docs/06 §6, D2)."""

import datetime
import uuid
from typing import Any

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.enums import CareType, ForecastMethod, FundingSource, RiskClass, text_enum


class Forecast(Base):
    """One stored forecast per line_key (contract, care_type, source, service_group)
    x horizon month. Explanation string is mandatory (docs/04 FORESEE)."""

    __tablename__ = "forecasts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    # line_key components
    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contracts.id"), index=True)
    care_type: Mapped[CareType] = mapped_column(text_enum(CareType), index=True)
    funding_source: Mapped[FundingSource] = mapped_column(text_enum(FundingSource), index=True)
    service_group: Mapped[str | None] = mapped_column(String(128))
    # forecast payload
    as_of: Mapped[datetime.date] = mapped_column(Date, index=True)
    horizon_month: Mapped[str] = mapped_column(String(7))  # YYYY-MM
    method: Mapped[ForecastMethod] = mapped_column(text_enum(ForecastMethod))
    value_qty: Mapped[int] = mapped_column(Integer)
    value_amount: Mapped[int] = mapped_column(BigInteger)  # whole tenge
    ci_low: Mapped[int] = mapped_column(BigInteger)  # whole tenge, p10
    ci_high: Mapped[int] = mapped_column(BigInteger)  # whole tenge, p90
    explanation: Mapped[str] = mapped_column(Text)
    inputs_hash: Mapped[str] = mapped_column(String(64))


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    # line_key components
    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contracts.id"), index=True)
    care_type: Mapped[CareType] = mapped_column(text_enum(CareType), index=True)
    funding_source: Mapped[FundingSource] = mapped_column(text_enum(FundingSource), index=True)
    service_group: Mapped[str | None] = mapped_column(String(128))
    # assessment payload
    as_of: Mapped[datetime.date] = mapped_column(Date, index=True)
    risk_class: Mapped[RiskClass] = mapped_column("class", text_enum(RiskClass), index=True)
    gap_amount: Mapped[int] = mapped_column(BigInteger, default=0)  # whole tenge
    burn_out_date: Mapped[datetime.date | None] = mapped_column(Date)
    recommendation: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
