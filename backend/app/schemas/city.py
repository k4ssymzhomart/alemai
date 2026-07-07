"""City panel API schemas (docs/05 §5, C5 — curator sees aggregates only)."""

import datetime
import uuid

from pydantic import Field

from app.schemas.common import APIModel


class CityClinicOut(APIModel):
    org_id: uuid.UUID
    name_kk: str
    name_ru: str
    execution_pct: float = 0.0
    composite_risk_score: float = 0.0
    critical_risk_count: int = 0
    forecast_gap: int = Field(default=0, description="whole tenge")


class CityOverviewOut(APIModel):
    as_of: datetime.date | None = None
    clinics: list[CityClinicOut] = []
