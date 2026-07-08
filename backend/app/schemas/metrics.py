"""Metrics API schemas — the stable frontend contract (shared contract C5).

Money is whole-tenge ``int``; ``as_of``/``period`` are ``"YYYY-MM"`` strings.
The ``forecast_*``/``risk_*``/``burn_out_date`` fields are typed Optional and
stay ``null`` until P6 wires the forecast engine — the frontend can bind to
them today without a later shape change.
"""

import datetime

from pydantic import Field

from app.models.enums import RiskClass
from app.schemas.common import APIModel


class OverviewOut(APIModel):
    """Hero KPIs for the Overview screen (docs/04 §2 screen 1)."""

    year: int
    as_of: str | None = Field(default=None, description="YYYY-MM; null when the year has no claims")
    plan_amount_year: int = Field(default=0, description="whole tenge")
    plan_amount_ytd: int = 0
    fact_amount_ytd: int = Field(default=0, description="claims accepted+paid (C4)")
    billed_amount_ytd: int = 0
    rejected_amount_ytd: int = 0
    rejected_amount_mtd: int = Field(default=0, description="rejected in the as_of month only")
    execution_pct_ytd: float = 0.0
    forecast_amount_year: int | None = None  # P6
    forecast_gap: int | None = None  # P6
    risk_count: int | None = None  # P6
    lines_total: int = 0


class LineItemOut(APIModel):
    """One contract line with YTD aggregates (Overview drill-down table)."""

    line_key: str = Field(description="C1: contract_id:care_type:funding_source:service_group|-")
    contract_id: str
    year: int
    care_type: str
    funding_source: str
    service_group: str = Field(description="'' when the line has no service group")
    plan_qty_year: int = 0
    plan_amount_year: int = Field(default=0, description="whole tenge")
    plan_amount_ytd: int = 0
    fact_qty_ytd: int = 0
    fact_amount_ytd: int = 0
    billed_amount_ytd: int = 0
    rejected_amount_ytd: int = 0
    execution_pct_ytd: float = 0.0
    forecast_amount_year: int | None = None  # P6
    forecast_gap: int | None = Field(
        default=None, description="plan_amount_year - forecast_amount_year"
    )
    forecast_explanation: dict[str, str] | None = Field(
        default=None, description="{ru, kk} — Passport «Почему» (seeded forecasts.explanation)"
    )
    risk_class: RiskClass | None = None  # P6
    burn_out_date: datetime.date | None = None  # P6
    recommendation: dict[str, str] | None = Field(
        default=None, description="{ru, kk} — Passport action (risk_assessments.recommendation)"
    )


class LinesOut(APIModel):
    """C5 /metrics/lines: items sorted by plan_amount_year DESC."""

    items: list[LineItemOut] = []
    total: int = 0
    year: int
    as_of: str | None = None


class MonthlyPointOut(APIModel):
    """One month of a line's plan/fact series (zeros where no data)."""

    month: int = Field(ge=1, le=12)
    period: str = Field(description="YYYY-MM")
    plan_qty: int = 0
    plan_amount: int = Field(default=0, description="whole tenge")
    fact_qty: int = 0
    fact_amount: int = 0
    billed_amount: int = 0
    rejected_amount: int = 0
    cumulative_plan_amount: int = 0
    cumulative_fact_amount: int = 0


class LineMonthlyOut(APIModel):
    """C5 /metrics/line/{line_key}/monthly: always all 12 months."""

    line_key: str
    year: int
    months: list[MonthlyPointOut] = []


class WaterfallStepOut(APIModel):
    """One step of plan -> billed -> снято -> paid waterfall."""

    stage: str
    amount: int = Field(default=0, description="whole tenge")


class WaterfallOut(APIModel):
    period: str | None = None
    steps: list[WaterfallStepOut] = []
