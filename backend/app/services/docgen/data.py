"""Live-data context for document generation (Epic D, P7′).

Every number in a generated .docx is pulled here from the same semantic layer
the dashboard uses (``app.services.metrics.queries``) — never invented, never
from the LLM. The two п. 19 grounds (пп. 25 остаток средств / пп. 26
факт-превышение) are computed from the seeded plan/fact/forecast figures.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.metrics import queries
from app.services.metrics.queries import LineData, OverviewData

# Care-type + funding display names (shared/glossary.csv terminology).
CARE_TYPE_RU: dict[str, str] = {
    "pmsp": "ПМСП (первичная медико-санитарная помощь)",
    "kdu": "КДУ (консультативно-диагностические услуги)",
    "day_hosp": "дневной стационар",
    "hosp": "круглосуточный стационар",
    "dent": "стоматологическая помощь",
    "screening": "скрининговые исследования",
    "ambulance": "скорая и неотложная помощь",
}
CARE_TYPE_KK: dict[str, str] = {
    "pmsp": "МСАК (медициналық-санитариялық алғашқы көмек)",
    "kdu": "КДҚ (консультациялық-диагностикалық қызметтер)",
    "day_hosp": "күндізгі стационар",
    "hosp": "тәуліктік стационар",
    "dent": "стоматологиялық көмек",
    "screening": "скринингтік зерттеулер",
    "ambulance": "жедел және шұғыл көмек",
}
FUNDING_RU: dict[str, str] = {"gobmp": "ГОБМП", "osms": "ОСМС"}
FUNDING_KK: dict[str, str] = {"gobmp": "ТМККК", "osms": "МӘМС"}


def care_type_name(code: str, lang: str) -> str:
    table = CARE_TYPE_KK if lang == "kk" else CARE_TYPE_RU
    return table.get(code, code)


def funding_name(code: str, lang: str) -> str:
    table = FUNDING_KK if lang == "kk" else FUNDING_RU
    return table.get(code, code.upper())


class LineNotFoundError(ValueError):
    """The requested line_key does not exist in the seeded contract year."""


@dataclass(frozen=True, slots=True)
class ObrashenieContext:
    """Everything the «Обращение в Фонд» template needs, all from live data."""

    line: LineData
    overview: OverviewData
    year: int
    as_of: str | None
    # п. 19 пп. 26) — прогнозное факт-превышение плана по линии (₸, >=0).
    fact_over_plan: int
    # п. 19 пп. 25) — свободный остаток средств по договору (₸, >=0).
    free_remainder: int
    # Requested additional volume (₸) = fact_over_plan when the line over-runs.
    requested_amount: int


def get_obrashenie_context(session: Session, line_key: str) -> ObrashenieContext:
    """Resolve the line + contract figures for the обращение (P7′ / EC-8/EC-9)."""
    parsed = queries.parse_line_key(line_key)
    year = queries.default_year(session)
    if year is None:
        raise LineNotFoundError("no seeded contract year")
    as_of, items = queries.lines(session, year, contract_id=parsed.contract_id)
    canonical = str(parsed)
    line = next((it for it in items if it.line_key == canonical), None)
    if line is None:
        raise LineNotFoundError(line_key)

    overview = queries.overview(session, year)
    forecast = line.forecast_amount_year
    fact_over_plan = (
        max(0, forecast - line.plan_amount_year) if forecast is not None else 0
    )
    free_remainder = max(0, overview.forecast_gap or 0)
    return ObrashenieContext(
        line=line,
        overview=overview,
        year=year,
        as_of=as_of,
        fact_over_plan=fact_over_plan,
        free_remainder=free_remainder,
        requested_amount=fact_over_plan,
    )


@dataclass(frozen=True, slots=True)
class MonthlyReportContext:
    """Aggregate + per-line figures for the kk/ru month management report."""

    year: int
    month: int
    period: str
    as_of: str | None
    overview: OverviewData
    lines: list[LineData]
    risk_lines: list[LineData]


def get_monthly_report_context(
    session: Session, year: int, month: int
) -> MonthlyReportContext:
    """Overview + per-line snapshot for the requested reporting month."""
    resolved = year or queries.default_year(session) or year
    as_of, items = queries.lines(session, resolved)
    overview = queries.overview(session, resolved)
    risk_lines = [
        it
        for it in items
        if it.risk_class is not None and it.risk_class.value != "on_track"
    ]
    return MonthlyReportContext(
        year=resolved,
        month=month,
        period=f"{resolved}-{month:02d}",
        as_of=as_of,
        overview=overview,
        lines=items,
        risk_lines=risk_lines,
    )
