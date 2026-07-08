"""Typed read layer over ``mv_line_execution`` (shared contracts C1, C2, C4, C5).

Every dashboard number comes from the materialized view (docs/05 §4, NFR <2s);
nothing here scans the raw ``claims`` table. Sessions come from ``app.db``; no
engine is created at import time.

YTD semantics (C4): for a contract year, ``as_of`` = MAX(period) among that
year's claims; YTD aggregates cover months 1..as_of_month; fact =
accepted+paid (already folded into the MV ``fact_*`` columns);
``execution_pct_ytd`` = fact/plan*100 (0 when plan is 0).
"""

from __future__ import annotations

import datetime
import json
import uuid
from dataclasses import dataclass

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.models.analytics import Forecast, RiskAssessment
from app.models.enums import RiskClass

# ---------------------------------------------------------------------------
# line_key helpers (contract C1):
#   "{contract_id}:{care_type}:{funding_source}:{service_group or '-'}"
# ---------------------------------------------------------------------------


class LineKeyError(ValueError):
    """A line_key string that does not follow contract C1."""


@dataclass(frozen=True, slots=True)
class ParsedLineKey:
    """A validated, normalized line identity (service_group '' = none)."""

    contract_id: uuid.UUID
    care_type: str
    funding_source: str
    service_group: str  # '' when the line has no service group ('-' in string form)

    def __str__(self) -> str:
        return format_line_key(
            self.contract_id, self.care_type, self.funding_source, self.service_group
        )


def format_line_key(
    contract_id: uuid.UUID | str,
    care_type: str,
    funding_source: str,
    service_group: str | None,
) -> str:
    """Render the C1 string form; empty/None service_group becomes '-'."""
    return f"{contract_id}:{care_type}:{funding_source}:{service_group or '-'}"


def parse_line_key(line_key: str) -> ParsedLineKey:
    """Parse a C1 line_key; raises :class:`LineKeyError` on any malformation.

    Splits on the first three ':' only — a service_group may itself contain
    ':'. '-' (and '') normalize to '' to match the MV's COALESCEd column (C2).
    """
    parts = line_key.split(":", 3)
    if len(parts) != 4 or not all(parts[:3]):
        raise LineKeyError(
            "expected 'contract_id:care_type:funding_source:service_group', "
            f"got {line_key!r}"
        )
    raw_contract_id, care_type, funding_source, service_group = parts
    try:
        contract_id = uuid.UUID(raw_contract_id)
    except ValueError as exc:
        raise LineKeyError(f"contract_id {raw_contract_id!r} is not a UUID") from exc
    return ParsedLineKey(
        contract_id=contract_id,
        care_type=care_type,
        funding_source=funding_source,
        service_group="" if service_group == "-" else service_group,
    )


# ---------------------------------------------------------------------------
# mv_line_execution (contract C2) — lightweight Core table, no metadata bind
# ---------------------------------------------------------------------------

_MV = sa.table(
    "mv_line_execution",
    sa.column("contract_id", sa.Uuid()),
    sa.column("org_id", sa.Uuid()),
    sa.column("year", sa.Integer()),
    sa.column("care_type", sa.Text()),
    sa.column("funding_source", sa.Text()),
    sa.column("service_group", sa.Text()),
    sa.column("month", sa.Integer()),
    sa.column("period", sa.Text()),
    sa.column("plan_qty", sa.BigInteger()),
    sa.column("plan_amount", sa.BigInteger()),
    sa.column("fact_qty", sa.BigInteger()),
    sa.column("fact_amount", sa.BigInteger()),
    sa.column("billed_qty", sa.BigInteger()),
    sa.column("billed_amount", sa.BigInteger()),
    sa.column("rejected_qty", sa.BigInteger()),
    sa.column("rejected_amount", sa.BigInteger()),
    sa.column("paid_qty", sa.BigInteger()),
    sa.column("paid_amount", sa.BigInteger()),
    sa.column("mis_only_qty", sa.BigInteger()),
    sa.column("mis_only_amount", sa.BigInteger()),
)


def _claim_activity() -> sa.ColumnElement[bool]:
    """True for MV rows that carry at least one claim (any of the 5 statuses).

    ``billed`` covers submitted/accepted/paid; rejected and mis_only cover the
    rest, so a grain-month has claims iff one of these sums is > 0 (claims
    carry qty >= 1; amounts kept as a belt-and-braces OR).
    """
    mv = _MV.c
    return sa.or_(
        (mv.billed_qty + mv.rejected_qty + mv.mis_only_qty) > 0,
        (mv.billed_amount + mv.rejected_amount + mv.mis_only_amount) > 0,
    )


def _bigint_sum(column: sa.ColumnClause[int]) -> sa.ColumnElement[int]:
    """SUM over the whole year, NULL-safe, cast back from numeric to bigint."""
    return sa.cast(sa.func.coalesce(sa.func.sum(column), 0), sa.BigInteger())


def _ytd_sum(column: sa.ColumnClause[int], as_of_month: int) -> sa.ColumnElement[int]:
    """SUM over months 1..as_of_month (C4); as_of_month=0 yields 0."""
    summed = sa.func.sum(column).filter(_MV.c.month <= as_of_month)
    return sa.cast(sa.func.coalesce(summed, 0), sa.BigInteger())


def execution_pct(fact_amount: int, plan_amount: int) -> float:
    """C4: fact/plan*100 rounded to 2 decimals; 0.0 when plan is 0."""
    return round(fact_amount / plan_amount * 100, 2) if plan_amount else 0.0


# ---------------------------------------------------------------------------
# Result rows (plain dataclasses — pydantic schemas validate from these)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class OverviewData:
    year: int
    as_of: str | None
    plan_amount_year: int
    plan_amount_ytd: int
    fact_amount_ytd: int
    billed_amount_ytd: int
    rejected_amount_ytd: int
    rejected_amount_mtd: int
    execution_pct_ytd: float
    lines_total: int
    # P6/F2 read-side — null when Epic B seeded no forecast/risk rows for the year.
    forecast_amount_year: int | None = None
    forecast_gap: int | None = None  # plan_amount_year - forecast_amount_year
    risk_count: int | None = None  # lines whose risk_class is not on_track


@dataclass(frozen=True, slots=True)
class LineData:
    line_key: str
    contract_id: str
    year: int
    care_type: str
    funding_source: str
    service_group: str
    plan_qty_year: int
    plan_amount_year: int
    plan_amount_ytd: int
    fact_qty_ytd: int
    fact_amount_ytd: int
    billed_amount_ytd: int
    rejected_amount_ytd: int
    execution_pct_ytd: float
    # P6/F2 read-side (per-line forecast + risk grain, seeded by Epic B).
    forecast_amount_year: int | None = None
    forecast_gap: int | None = None  # plan_amount_year - forecast_amount_year
    forecast_explanation: dict[str, str] | None = None  # {ru, kk} — Passport «Почему»
    risk_class: RiskClass | None = None
    burn_out_date: datetime.date | None = None
    recommendation: dict[str, str] | None = None  # {ru, kk} — Passport «Что делать»


@dataclass(frozen=True, slots=True)
class LineProjection:
    """Seeded forecast + risk for one line grain (P6/F2 read-side)."""

    forecast_amount_year: int | None = None
    forecast_explanation: dict[str, str] | None = None
    risk_class: RiskClass | None = None
    burn_out_date: datetime.date | None = None
    recommendation: dict[str, str] | None = None


@dataclass(frozen=True, slots=True)
class MonthData:
    month: int
    period: str
    plan_qty: int
    plan_amount: int
    fact_qty: int
    fact_amount: int
    billed_amount: int
    rejected_amount: int
    cumulative_plan_amount: int
    cumulative_fact_amount: int


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------


def _parse_bilingual(raw: object) -> dict[str, str] | None:
    """Coerce a seeded {ru, kk} blob (JSONB dict or JSON-text) into a plain dict.

    ``forecasts.explanation`` is stored as Text holding a JSON object;
    ``risk_assessments.recommendation`` is JSONB (already a dict). Malformed or
    plain-string values degrade to ``{"ru": <text>}`` so the frontend never 500s.
    """
    if raw is None:
        return None
    if isinstance(raw, dict):
        return {str(k): str(v) for k, v in raw.items()}
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except (ValueError, TypeError):
            return {"ru": raw}
        if isinstance(parsed, dict):
            return {str(k): str(v) for k, v in parsed.items()}
        return {"ru": raw}
    return None


def _grain_key(
    contract_id: object, care_type: object, funding_source: object, service_group: object
) -> tuple[str, str, str, str]:
    """Line grain key normalized to the MV form (service_group '' == none)."""
    return (str(contract_id), str(care_type), str(funding_source), str(service_group or ""))


GrainKey = tuple[str, str, str, str]


def line_projections(session: Session, year: int) -> dict[GrainKey, LineProjection]:
    """Seeded forecast + risk keyed by line grain (P6/F2), latest ``as_of`` wins.

    Forecasts are filtered to the year-end horizon (``YYYY-12``); risk to the
    same calendar year. Returns ``{}`` when Epic B seeded nothing for the year.
    """
    horizon = f"{year}-12"
    forecast_by_grain: dict[GrainKey, Forecast] = {}
    for f in session.execute(
        sa.select(Forecast).where(Forecast.horizon_month == horizon).order_by(Forecast.as_of)
    ).scalars():
        key = _grain_key(f.contract_id, f.care_type, f.funding_source, f.service_group)
        forecast_by_grain[key] = f

    risk_by_grain: dict[GrainKey, RiskAssessment] = {}
    for r in session.execute(
        sa.select(RiskAssessment)
        .where(sa.extract("year", RiskAssessment.as_of) == year)
        .order_by(RiskAssessment.as_of)
    ).scalars():
        key = _grain_key(r.contract_id, r.care_type, r.funding_source, r.service_group)
        risk_by_grain[key] = r

    projections: dict[GrainKey, LineProjection] = {}
    for key in set(forecast_by_grain) | set(risk_by_grain):
        f = forecast_by_grain.get(key)
        r = risk_by_grain.get(key)
        projections[key] = LineProjection(
            forecast_amount_year=int(f.value_amount) if f else None,
            forecast_explanation=_parse_bilingual(f.explanation) if f else None,
            risk_class=r.risk_class if r else None,
            burn_out_date=r.burn_out_date if r else None,
            recommendation=_parse_bilingual(r.recommendation) if r else None,
        )
    return projections


def default_year(session: Session) -> int | None:
    """Latest year with claim activity; else latest plan year; else None."""
    mv = _MV.c
    year = session.execute(
        sa.select(sa.func.max(mv.year)).where(_claim_activity())
    ).scalar()
    if year is None:
        year = session.execute(sa.select(sa.func.max(mv.year))).scalar()
    return int(year) if year is not None else None


def resolve_as_of(session: Session, year: int) -> str | None:
    """C4 as_of: MAX(period) among the year's claims; None when it has none.

    Computed from the MV instead of the 500k-row ``claims`` table: every claim
    lands in exactly one status bucket, so MAX(period) over claim-active MV
    rows (see :func:`_claim_activity`) equals MAX(period) over claims.
    """
    mv = _MV.c
    period = session.execute(
        sa.select(sa.func.max(mv.period)).where(mv.year == year, _claim_activity())
    ).scalar()
    return str(period) if period is not None else None


def overview(session: Session, year: int) -> OverviewData:
    """Hero KPIs for one contract year (C5 /metrics/overview).

    A year with no claims is not an error: all YTD aggregates are 0 and
    as_of is None (documented API choice — the dashboard renders an empty
    state, 404 would break the stable frontend contract).
    """
    mv = _MV.c
    as_of = resolve_as_of(session, year)
    as_of_month = int(as_of[-2:]) if as_of else 0
    mtd = sa.func.sum(mv.rejected_amount).filter(mv.month == as_of_month)
    grain = sa.tuple_(mv.contract_id, mv.care_type, mv.funding_source, mv.service_group)
    row = session.execute(
        sa.select(
            _bigint_sum(mv.plan_amount).label("plan_amount_year"),
            _ytd_sum(mv.plan_amount, as_of_month).label("plan_amount_ytd"),
            _ytd_sum(mv.fact_amount, as_of_month).label("fact_amount_ytd"),
            _ytd_sum(mv.billed_amount, as_of_month).label("billed_amount_ytd"),
            _ytd_sum(mv.rejected_amount, as_of_month).label("rejected_amount_ytd"),
            sa.cast(sa.func.coalesce(mtd, 0), sa.BigInteger()).label("rejected_amount_mtd"),
            sa.func.count(sa.distinct(grain)).label("lines_total"),
        ).where(mv.year == year)
    ).one()
    plan_amount_year = int(row.plan_amount_year)
    projections = line_projections(session, year)
    forecast_values = [
        p.forecast_amount_year for p in projections.values() if p.forecast_amount_year is not None
    ]
    forecast_amount_year = sum(forecast_values) if forecast_values else None
    forecast_gap = (
        plan_amount_year - forecast_amount_year if forecast_amount_year is not None else None
    )
    has_risk = any(p.risk_class is not None for p in projections.values())
    risk_count = (
        sum(
            1
            for p in projections.values()
            if p.risk_class is not None and p.risk_class != RiskClass.on_track
        )
        if has_risk
        else None
    )
    return OverviewData(
        year=year,
        as_of=as_of,
        plan_amount_year=plan_amount_year,
        plan_amount_ytd=int(row.plan_amount_ytd),
        fact_amount_ytd=int(row.fact_amount_ytd),
        billed_amount_ytd=int(row.billed_amount_ytd),
        rejected_amount_ytd=int(row.rejected_amount_ytd),
        rejected_amount_mtd=int(row.rejected_amount_mtd),
        execution_pct_ytd=execution_pct(int(row.fact_amount_ytd), int(row.plan_amount_ytd)),
        lines_total=int(row.lines_total),
        forecast_amount_year=forecast_amount_year,
        forecast_gap=forecast_gap,
        risk_count=risk_count,
    )


def lines(
    session: Session,
    year: int,
    *,
    funding_source: str | None = None,
    care_type: str | None = None,
    contract_id: uuid.UUID | None = None,
) -> tuple[str | None, list[LineData]]:
    """Per-line YTD aggregates (C5 /metrics/lines), plan_amount_year DESC.

    Returns ``(as_of, items)``; the C4 as_of is resolved once for the whole
    year (not per line) so all rows share the same YTD window.
    """
    mv = _MV.c
    as_of = resolve_as_of(session, year)
    as_of_month = int(as_of[-2:]) if as_of else 0
    plan_amount_year = _bigint_sum(mv.plan_amount).label("plan_amount_year")
    stmt = (
        sa.select(
            mv.contract_id,
            mv.care_type,
            mv.funding_source,
            mv.service_group,
            _bigint_sum(mv.plan_qty).label("plan_qty_year"),
            plan_amount_year,
            _ytd_sum(mv.plan_amount, as_of_month).label("plan_amount_ytd"),
            _ytd_sum(mv.fact_qty, as_of_month).label("fact_qty_ytd"),
            _ytd_sum(mv.fact_amount, as_of_month).label("fact_amount_ytd"),
            _ytd_sum(mv.billed_amount, as_of_month).label("billed_amount_ytd"),
            _ytd_sum(mv.rejected_amount, as_of_month).label("rejected_amount_ytd"),
        )
        .where(mv.year == year)
        .group_by(mv.contract_id, mv.care_type, mv.funding_source, mv.service_group)
        .order_by(
            plan_amount_year.desc(),
            mv.care_type,
            mv.funding_source,
            mv.service_group,
            mv.contract_id,
        )
    )
    if funding_source is not None:
        stmt = stmt.where(mv.funding_source == funding_source)
    if care_type is not None:
        stmt = stmt.where(mv.care_type == care_type)
    if contract_id is not None:
        stmt = stmt.where(mv.contract_id == contract_id)

    projections = line_projections(session, year)
    items: list[LineData] = []
    for row in session.execute(stmt):
        plan_amount_year = int(row.plan_amount_year)
        proj = projections.get(
            _grain_key(row.contract_id, row.care_type, row.funding_source, row.service_group),
            LineProjection(),
        )
        forecast_gap = (
            plan_amount_year - proj.forecast_amount_year
            if proj.forecast_amount_year is not None
            else None
        )
        items.append(
            LineData(
                line_key=format_line_key(
                    row.contract_id, row.care_type, row.funding_source, row.service_group
                ),
                contract_id=str(row.contract_id),
                year=year,
                care_type=row.care_type,
                funding_source=row.funding_source,
                service_group=row.service_group,
                plan_qty_year=int(row.plan_qty_year),
                plan_amount_year=plan_amount_year,
                plan_amount_ytd=int(row.plan_amount_ytd),
                fact_qty_ytd=int(row.fact_qty_ytd),
                fact_amount_ytd=int(row.fact_amount_ytd),
                billed_amount_ytd=int(row.billed_amount_ytd),
                rejected_amount_ytd=int(row.rejected_amount_ytd),
                execution_pct_ytd=execution_pct(int(row.fact_amount_ytd), int(row.plan_amount_ytd)),
                forecast_amount_year=proj.forecast_amount_year,
                forecast_gap=forecast_gap,
                forecast_explanation=proj.forecast_explanation,
                risk_class=proj.risk_class,
                burn_out_date=proj.burn_out_date,
                recommendation=proj.recommendation,
            )
        )
    return as_of, items


def line_monthly(session: Session, key: ParsedLineKey, year: int) -> list[MonthData] | None:
    """All 12 months for one line (C5), zero-filled, with running cumulatives.

    Returns None when the line grain exists in no year at all (-> API 404).
    A known line queried for a year without data returns 12 zero months —
    same "no data is not an error" choice as :func:`overview`.
    """
    mv = _MV.c
    grain = sa.and_(
        mv.contract_id == key.contract_id,
        mv.care_type == key.care_type,
        mv.funding_source == key.funding_source,
        mv.service_group == key.service_group,
    )
    known = session.execute(
        sa.select(sa.literal(1)).select_from(_MV).where(grain).limit(1)
    ).first()
    if known is None:
        return None

    stmt = sa.select(
        mv.month,
        mv.plan_qty,
        mv.plan_amount,
        mv.fact_qty,
        mv.fact_amount,
        mv.billed_amount,
        mv.rejected_amount,
    ).where(grain, mv.year == year)
    by_month = {int(row.month): row for row in session.execute(stmt)}

    months: list[MonthData] = []
    cumulative_plan = 0
    cumulative_fact = 0
    for month in range(1, 13):
        row = by_month.get(month)
        plan_amount = int(row.plan_amount) if row else 0
        fact_amount = int(row.fact_amount) if row else 0
        cumulative_plan += plan_amount
        cumulative_fact += fact_amount
        months.append(
            MonthData(
                month=month,
                period=f"{year}-{month:02d}",
                plan_qty=int(row.plan_qty) if row else 0,
                plan_amount=plan_amount,
                fact_qty=int(row.fact_qty) if row else 0,
                fact_amount=fact_amount,
                billed_amount=int(row.billed_amount) if row else 0,
                rejected_amount=int(row.rejected_amount) if row else 0,
                cumulative_plan_amount=cumulative_plan,
                cumulative_fact_amount=cumulative_fact,
            )
        )
    return months
