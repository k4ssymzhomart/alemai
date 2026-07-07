"""Forecast API schemas (docs/05 §5, methodology docs/06 §6)."""

import datetime
import uuid

from pydantic import Field

from app.models.enums import ForecastMethod
from app.schemas.common import APIModel, LineKey


class ForecastOut(APIModel):
    id: uuid.UUID
    line_key: LineKey
    as_of: datetime.date
    horizon_month: str = Field(description="YYYY-MM")
    method: ForecastMethod
    value_qty: int = 0
    value_amount: int = Field(default=0, description="whole tenge")
    ci_low: int = Field(default=0, description="whole tenge, p10")
    ci_high: int = Field(default=0, description="whole tenge, p90")
    explanation: str = Field(description="mandatory 'почему' sentence (docs/04 FORESEE)")


class ForecastsOut(APIModel):
    as_of: datetime.date | None = None
    forecasts: list[ForecastOut] = []


class RecomputeResult(APIModel):
    status: str = "scheduled"
    lines_recomputed: int = 0
