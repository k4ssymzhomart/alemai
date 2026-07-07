"""Metrics endpoints (docs/05 §5) — read from mv_line_execution when built."""

from fastapi import APIRouter

from app.api.deps import FiltersDep
from app.schemas.metrics import LineMonthlyOut, LinesOut, OverviewOut, WaterfallOut

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/overview", response_model=OverviewOut)
def get_overview(filters: FiltersDep) -> OverviewOut:
    """Hero KPIs: execution % YTD, forecast gap, risk counts, снятия MTD."""
    return OverviewOut()


@router.get("/lines", response_model=LinesOut)
def get_lines(filters: FiltersDep) -> LinesOut:
    """Per-line plan/fact/forecast/risk table for the Overview screen."""
    return LinesOut(lines=[])


@router.get("/line/{line_key}/monthly", response_model=LineMonthlyOut)
def get_line_monthly(line_key: str) -> LineMonthlyOut:
    """Monthly plan/fact/forecast series for one contract line."""
    return LineMonthlyOut(line_key=line_key, points=[])


@router.get("/waterfall", response_model=WaterfallOut)
def get_waterfall(filters: FiltersDep) -> WaterfallOut:
    """Plan -> billed -> снято -> paid money waterfall."""
    return WaterfallOut(period=filters.period, steps=[])
