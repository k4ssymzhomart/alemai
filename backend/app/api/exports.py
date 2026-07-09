"""XLSX export endpoints — EPIC F2 (ST-3, docs/17: economists live in Excel).

Every export is built from the same queries the screens render — no number
reaches the file that the system didn't compute. House style + file naming law
live in :mod:`app.services.exports.xlsx`.
"""

import datetime
import uuid
from typing import Annotated

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.models.claim import Claim
from app.models.imports import ImportFile, QuarantineRow
from app.models.rules import Finding, RuleRun
from app.services import reconcile as reconcile_svc
from app.services.exports.xlsx import (
    DATE_FMT,
    PCT_FMT,
    TENGE_FMT,
    Column,
    build_xlsx,
    export_filename,
    xlsx_response,
)
from app.services.ingest.registry import (
    DAMUMED_REGISTRY_PRESET,
    FUNDING_LABEL_BY_SOURCE,
)
from app.services.ingest.samples import CARE_TYPE_LABEL_RU
from app.services.metrics import queries
from app.services.rules_engine import ekd, engine

router = APIRouter(prefix="/exports", tags=["exports"])

DbDep = Annotated[Session, Depends(get_db)]

_SEVERITY_ORDER = {"block": 0, "warn": 1, "yellow": 2, "info": 3}
_SEVERITY_RU = {
    "block": "блокер — исключить из счёт-реестра",
    "warn": "риск — проверить",
    "yellow": "жёлтый — фиксация без снятия (0 ₸)",
    "info": "наблюдение",
}
_RISK_RU = {
    "critical_under": "критическое недоосвоение",
    "under_risk": "риск недоосвоения",
    "on_track": "в графике",
    "over_risk": "риск перевыполнения",
    "critical_over": "критическое перевыполнение",
}

RECONCILE_ROW_CAP = 5000


def _latest_run(db: Session, scope: str) -> RuleRun:
    """Latest rule run for the scope; runs the engine when none exists yet."""
    run = db.execute(
        sa.select(RuleRun).where(RuleRun.scope == scope)
        .order_by(RuleRun.started_at.desc()).limit(1)
    ).scalar_one_or_none()
    if run is not None:
        return run
    result = engine.run(db, scope=scope)
    db.commit()
    run = db.get(RuleRun, result.run_id)
    assert run is not None
    return run


@router.get("/prebilling.xlsx")
def export_prebilling(
    db: DbDep,
    scope: Annotated[str, Query(description="e.g. 'period:2025-11'")] = "period:2025-11",
) -> StreamingResponse:
    """«Экспорт исключений»: the fix list Дана hands to врачи (ST-3)."""
    run = _latest_run(db, scope)
    kpn = get_settings().kpn_tenge
    rows_db = db.execute(
        sa.select(Finding, Claim)
        .join(Claim, Claim.id == Finding.claim_id)
        .where(Finding.run_id == run.id)
    ).all()

    body: list[list] = []
    for finding, claim in rows_db:
        details = finding.details or {}
        ekd_code = str(details.get("ekd_code") or "")
        billed = int(details.get("amount_billed") or claim.amount)
        sanction = (
            ekd.sanction_total(ekd_code, str(claim.care_type), billed, kpn)
            if ekd_code else 0
        )
        body.append([
            _SEVERITY_ORDER.get(str(details.get("severity")), 9),  # sort key, dropped
            finding.rule_code,
            ekd_code,
            _SEVERITY_RU.get(str(details.get("severity")), str(details.get("severity"))),
            str(finding.claim_id),
            claim.patient_id,
            claim.service_code,
            claim.service_name,
            claim.date_start,
            billed,
            int(finding.amount_at_risk),
            sanction,
            str(details.get("message_ru") or ""),
        ])
    body.sort(key=lambda r: (r[0], -r[11]))
    rows = [r[1:] for r in body]

    columns = [
        Column("Правило", 9),
        Column("Код ЕКД", 9),
        Column("Статус проверки", 34),
        Column("Case ID (позиция реестра)", 38),
        Column("Пациент (хэш)", 24),
        Column("Код услуги", 12),
        Column("Наименование услуги", 36),
        Column("Дата услуги", 13, DATE_FMT),
        Column("Предъявлено, ₸", 16, TENGE_FMT),
        Column("Под риском, ₸", 15, TENGE_FMT),
        Column("Санкция ЕКД, ₸", 16, TENGE_FMT),
        Column("Сообщение правила", 60),
    ]
    period = scope.partition(":")[2] or scope
    data = build_xlsx(f"Исключения {period}", columns, rows)
    return xlsx_response(data, export_filename("prebilling"))


@router.get("/reconcile-bucket/{bucket_no}.xlsx")
def export_reconcile_bucket(
    db: DbDep, bucket_no: Annotated[int, Path(ge=1, le=4)]
) -> StreamingResponse:
    """Per-bucket claim rows (сверка трёх миров, ST-4)."""
    bucket_rows = reconcile_svc.bucket_rows(db, bucket_no, limit=RECONCILE_ROW_CAP)
    rows: list[list] = [
        [i, str(r.claim_id), r.patient_id, r.service_code, r.service_name,
         r.date_start, r.amount, r.detail]
        for i, r in enumerate(bucket_rows, start=1)
    ]
    if len(bucket_rows) == RECONCILE_ROW_CAP:
        rows.append([None, f"… выгружены первые {RECONCILE_ROW_CAP} строк (по убыванию ₸)",
                     None, None, None, None, None, None])
    columns = [
        Column("№", 6),
        Column("Case ID", 38),
        Column("Пациент (хэш)", 24),
        Column("Код услуги", 12),
        Column("Наименование услуги", 36),
        Column("Дата услуги", 13, DATE_FMT),
        Column("Сумма, ₸", 14, TENGE_FMT),
        Column("Категория сверки", 30),
    ]
    data = build_xlsx(f"Сверка — бакет {bucket_no}", columns, rows)
    return xlsx_response(data, export_filename(f"reconcile_bucket{bucket_no}"))


@router.get("/overview.xlsx")
def export_overview(db: DbDep, year: int = 2026) -> StreamingResponse:
    """«Экспорт план/факт»: the grouped ledger with forecast + risk per line."""
    _as_of, items = queries.lines(db, year)
    rows: list[list] = [
        [
            CARE_TYPE_LABEL_RU.get(line.care_type, line.care_type),
            line.service_group or "—",
            FUNDING_LABEL_BY_SOURCE.get(line.funding_source, line.funding_source),
            line.plan_amount_year,
            line.plan_amount_ytd,
            line.fact_amount_ytd,
            line.execution_pct_ytd,
            line.forecast_amount_year,
            line.forecast_gap,
            _RISK_RU.get(str(line.risk_class or ""), ""),
            line.burn_out_date,
        ]
        for line in items
    ]
    columns = [
        Column("Вид помощи", 24),
        Column("Группа услуг", 14),
        Column("Источник", 10),
        Column("План на год, ₸", 16, TENGE_FMT),
        Column("План YTD, ₸", 15, TENGE_FMT),
        Column("Факт YTD, ₸", 15, TENGE_FMT),
        Column("Исполнение YTD, %", 18, PCT_FMT),
        Column("Прогноз на год, ₸", 17, TENGE_FMT),
        Column("Отклонение от плана, ₸", 21, TENGE_FMT),
        Column("Класс риска", 28),
        Column("Дата исчерпания объёма", 22, DATE_FMT),
    ]
    data = build_xlsx(f"План-факт {year}", columns, rows)
    return xlsx_response(data, export_filename("overview"))


@router.get("/quarantine/{file_id}.xlsx")
def export_quarantine(db: DbDep, file_id: uuid.UUID) -> StreamingResponse:
    """Quarantined rows of one import — the fix list for the МИС operator."""
    import_file = db.get(ImportFile, file_id)
    if import_file is None:
        raise HTTPException(status_code=404, detail="import file not found")
    q_rows = db.execute(
        sa.select(QuarantineRow)
        .where(QuarantineRow.import_file_id == file_id)
        .order_by(QuarantineRow.row_no)
    ).scalars().all()

    source_headers = [c.header for c in DAMUMED_REGISTRY_PRESET]
    rows: list[list] = []
    for q in q_rows:
        raw = q.raw or {}
        rows.append([q.row_no, "; ".join(q.errors or [])]
                    + [raw.get(h) for h in source_headers])
    columns = [Column("№ строки файла", 14), Column("Причины карантина", 60)]
    columns += [Column(h, 22) for h in source_headers]
    data = build_xlsx("Карантин", columns, rows)
    day = datetime.date.today()
    return xlsx_response(data, export_filename("quarantine", day))
