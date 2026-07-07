"""Metrics API schemas (docs/05 §5, semantic layer docs/06 §5)."""

import datetime

from pydantic import Field

from app.models.enums import CareType, FundingSource, RiskClass
from app.schemas.common import APIModel, LineKey


class OverviewOut(APIModel):
    """Hero KPIs for the Overview screen (docs/04 §2 screen 1)."""

    execution_pct_ytd: float = 0.0
    plan_amount_ytd: int = Field(default=0, description="whole tenge")
    fact_amount_ytd: int = Field(default=0, description="whole tenge")
    forecast_gap: int = Field(default=0, description="whole tenge")
    snyato_amount_mtd: int = Field(default=0, description="whole tenge")
    risk_count_by_class: dict[str, int] = {}
    as_of: datetime.date | None = None


class LineMetricsOut(APIModel):
    line_key: LineKey
    care_type: CareType
    funding_source: FundingSource
    service_group: str | None = None
    plan_qty: int = 0
    plan_amount: int = Field(default=0, description="whole tenge")
    fact_qty: int = 0
    fact_amount: int = Field(default=0, description="whole tenge")
    execution_pct: float = 0.0
    forecast_amount: int = Field(default=0, description="whole tenge")
    risk_class: RiskClass | None = None
    burn_out_date: datetime.date | None = None


class LinesOut(APIModel):
    lines: list[LineMetricsOut] = []


class MonthlyPointOut(APIModel):
    month: str = Field(description="YYYY-MM")
    plan_qty: int = 0
    plan_amount: int = Field(default=0, description="whole tenge")
    fact_qty: int = 0
    fact_amount: int = Field(default=0, description="whole tenge")
    forecast_amount: int | None = None


class LineMonthlyOut(APIModel):
    line_key: str
    points: list[MonthlyPointOut] = []


class WaterfallStepOut(APIModel):
    """One step of plan -> billed -> снято -> paid waterfall."""

    stage: str
    amount: int = Field(default=0, description="whole tenge")


class WaterfallOut(APIModel):
    period: str | None = None
    steps: list[WaterfallStepOut] = []
