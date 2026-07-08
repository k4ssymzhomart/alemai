"""Metrics endpoints (docs/05 §5) — served from mv_line_execution (C4/C5).

Missing-data semantics (deliberate choice, mirrored in the query layer): a
year with no claims is NOT a 404 — /overview and /lines return zeros with
``as_of=null`` so the dashboard renders an empty state instead of an error.
Only an unknown ``line_key`` 404s: the path names a resource that does not
exist in any year.

Query parameters go through Depends-wrapped provider functions (the same
pattern as :mod:`app.api.deps` — FastAPI 0.139 otherwise mis-reads pydantic
models in GET signatures as body params).
"""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import FiltersDep
from app.db import get_db
from app.schemas.metrics import (
    LineItemOut,
    LineMonthlyOut,
    LinesOut,
    MonthlyPointOut,
    OverviewOut,
    WaterfallOut,
)
from app.services.metrics import queries
from app.services.metrics.queries import LineKeyError

router = APIRouter(prefix="/metrics", tags=["metrics"])

DbDep = Annotated[Session, Depends(get_db)]

YearQuery = Annotated[
    int | None, Query(description="contract year, e.g. 2026; default = latest year with claims")
]


def _year_param(year: YearQuery = None) -> int | None:
    return year


YearDep = Annotated[int | None, Depends(_year_param)]


@dataclass(frozen=True)
class LinesParams:
    """Query params of GET /metrics/lines (C5)."""

    year: int | None
    funding_source: str | None
    care_type: str | None
    contract_id: str | None


def _lines_params(
    year: YearQuery = None,
    funding_source: Annotated[str | None, Query(description="gobmp|osms")] = None,
    care_type: Annotated[str | None, Query(description="pmsp|kdu|day_hosp|...")] = None,
    contract_id: Annotated[str | None, Query(description="contract UUID")] = None,
) -> LinesParams:
    return LinesParams(year, funding_source, care_type, contract_id)


LinesParamsDep = Annotated[LinesParams, Depends(_lines_params)]


def _resolve_year(db: Session, year: int | None) -> int:
    """Explicit ?year= wins; else latest year with claims; else current year."""
    if year is not None:
        return year
    resolved = queries.default_year(db)
    return resolved if resolved is not None else datetime.now(tz=UTC).year


@router.get("/overview", response_model=OverviewOut)
def get_overview(db: DbDep, year: YearDep) -> OverviewOut:
    """Hero KPIs: plan/fact/billed/rejected YTD, execution %, снятия MTD."""
    data = queries.overview(db, _resolve_year(db, year))
    return OverviewOut.model_validate(data)


@router.get("/lines", response_model=LinesOut)
def get_lines(db: DbDep, params: LinesParamsDep) -> LinesOut:
    """Per-line plan/fact table for the Overview screen, plan_amount_year DESC."""
    contract_id: uuid.UUID | None = None
    if params.contract_id is not None:
        try:
            contract_id = uuid.UUID(params.contract_id)
        except ValueError:
            raise HTTPException(status_code=422, detail="contract_id must be a UUID") from None
    year = _resolve_year(db, params.year)
    as_of, items = queries.lines(
        db,
        year,
        funding_source=params.funding_source,
        care_type=params.care_type,
        contract_id=contract_id,
    )
    return LinesOut(
        items=[LineItemOut.model_validate(item) for item in items],
        total=len(items),
        year=year,
        as_of=as_of,
    )


@router.get("/line/{line_key}/monthly", response_model=LineMonthlyOut)
def get_line_monthly(line_key: str, db: DbDep, year: YearDep) -> LineMonthlyOut:
    """Monthly plan/fact series for one line — all 12 months, zero-filled."""
    try:
        parsed = queries.parse_line_key(line_key)
    except LineKeyError as exc:
        # Malformed key == a line that cannot exist -> same 404 as unknown.
        raise HTTPException(status_code=404, detail=f"unknown line_key: {exc}") from exc
    resolved_year = _resolve_year(db, year)
    months = queries.line_monthly(db, parsed, resolved_year)
    if months is None:
        raise HTTPException(status_code=404, detail=f"unknown line_key: {line_key}")
    return LineMonthlyOut(
        line_key=str(parsed),  # canonical C1 form ('' service_group -> '-')
        year=resolved_year,
        months=[MonthlyPointOut.model_validate(month) for month in months],
    )


@router.get("/waterfall", response_model=WaterfallOut)
def get_waterfall(filters: FiltersDep) -> WaterfallOut:
    """Plan -> billed -> снято -> paid money waterfall."""
    return WaterfallOut(period=filters.period, steps=[])
