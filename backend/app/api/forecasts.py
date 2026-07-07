"""Forecast endpoints (docs/05 §5, methodology docs/06 §6)."""

import datetime
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import FiltersDep
from app.schemas.forecasts import ForecastsOut, RecomputeResult

router = APIRouter(prefix="/forecasts", tags=["forecasts"])

AsOfQuery = Annotated[datetime.date | None, Query(description="forecast snapshot date")]


@router.get("", response_model=ForecastsOut)
def list_forecasts(filters: FiltersDep, as_of: AsOfQuery = None) -> ForecastsOut:
    """Stored per-line forecasts with CI and mandatory explanation."""
    return ForecastsOut(as_of=as_of, forecasts=[])


@router.post("/recompute", response_model=RecomputeResult, status_code=202)
def recompute_forecasts() -> RecomputeResult:
    """Recompute all line forecasts. Stub: schedules nothing yet."""
    return RecomputeResult(status="scheduled", lines_recomputed=0)
