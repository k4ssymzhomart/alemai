"""Imports endpoints — EPIC F1/F3 (docs/05 §5, docs/17 ingest & exchange).

POST /imports/mis-registry is the demo beat: multipart XLSX/CSV → preset
mapping → validation/quarantine → idempotent upsert → auto rules run for the
detected period. Sample files are generated from the live DB (never committed
binaries) so the demo upload always reproduces the golden verdict.
"""

import uuid
from typing import Annotated

import sqlalchemy as sa
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import OptionalPrincipal
from app.db import get_db
from app.models.imports import ImportFile, QuarantineRow
from app.schemas.imports import (
    AnnexLineDiffOut,
    AnnexPreviewOut,
    ColumnMapOut,
    QuarantineOut,
    QuarantineRowOut,
    RegistryImportOut,
)
from app.services import events as events_svc
from app.services.exports.xlsx import xlsx_response
from app.services.ingest import samples
from app.services.ingest.annex import preview_annex
from app.services.ingest.registry import RegistryParseError, import_registry
from app.services.metrics.refresh import refresh_line_execution
from app.services.rules_engine import engine

router = APIRouter(prefix="/imports", tags=["imports"])

DbDep = Annotated[Session, Depends(get_db)]
FileDep = Annotated[UploadFile, File(description="XLSX/CSV выгрузка из МИС")]

MAX_UPLOAD_BYTES = 30 * 1024 * 1024
QUARANTINE_PREVIEW_CAP = 50

# Demo sample files, generated from the live DB (docs/17 F1/F3).
_SAMPLE_BUILDERS = {
    "registry_2025-11.xlsx": lambda db: samples.registry_sample(db, "2025-11"),
    "registry_broken.xlsx": lambda db: samples.registry_broken_sample(db, "2025-11"),
    "annex_2026.xlsx": lambda db: samples.annex_sample(db, 2026),
}


@router.post("/mis-registry", response_model=RegistryImportOut, status_code=201)
async def import_mis_registry(
    file: FileDep, db: DbDep, principal: OptionalPrincipal
) -> RegistryImportOut:
    """Import a МИС «реестр услуг» export; idempotent — re-upload adds nothing."""
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="файл больше 30 МБ")
    try:
        report = import_registry(db, file.filename or "registry.xlsx", data)
    except RegistryParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    # The dashboard reads mv_line_execution — refresh only when claims changed
    # (the golden-path upload matches everything, so this is skipped there).
    if report.updated or report.new:
        refresh_line_execution(db)
    events_svc.import_completed(
        db, principal, filename=report.filename, period=report.period_detected,
        rows_ok=report.rows_ok, quarantined=len(report.quarantine),
        new=report.new, matched=report.matched,
    )
    db.commit()

    rule_run_id = None
    rule_totals = None
    if report.period_detected and report.rows_ok:
        result = engine.run(db, scope=f"period:{report.period_detected}")
        rule_totals = result.totals_json()
        events_svc.rules_run_finished(
            db, principal, scope=result.scope, totals=rule_totals, triggered_by="import",
        )
        db.commit()
        rule_run_id = result.run_id

    return RegistryImportOut(
        file_id=report.file_id,
        filename=report.filename,
        preset=report.preset,
        period_detected=report.period_detected,
        rows_total=report.rows_total,
        rows_ok=report.rows_ok,
        matched=report.matched,
        updated=report.updated,
        new=report.new,
        quarantined=len(report.quarantine),
        control_sum=report.control_sum,
        claims_in_period=report.claims_in_period,
        mapping=[ColumnMapOut.model_validate(m, from_attributes=True)
                 for m in report.mapping],
        quarantine=[
            QuarantineRowOut(row_no=b.row_no, raw=b.raw, errors=b.errors)
            for b in report.quarantine[:QUARANTINE_PREVIEW_CAP]
        ],
        rule_run_id=rule_run_id,
        rule_totals=rule_totals,
    )


@router.post("/contract-annex", response_model=AnnexPreviewOut)
async def import_contract_annex(
    file: FileDep, db: DbDep, preview: int = 1, year: int = 2026
) -> AnnexPreviewOut:
    """Annex diff — PREVIEW ONLY, nothing is written (применение — в пилоте).

    ``preview`` is accepted for API-shape compatibility but commit is not
    implemented by design (docs/17 F3: the demo stops at the preview).
    """
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="файл больше 30 МБ")
    try:
        result = preview_annex(db, file.filename or "annex.xlsx", data, year)
    except RegistryParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return AnnexPreviewOut(
        filename=result.filename,
        year=result.year,
        lines=[AnnexLineDiffOut.model_validate(d, from_attributes=True)
               for d in result.lines],
        changed=result.changed,
        total_current=result.total_current,
        total_annex=result.total_annex,
        total_delta=result.total_delta,
        preview_only=True,
    )


@router.get("/samples/{filename}")
def download_sample(filename: str, db: DbDep) -> StreamingResponse:
    """Demo sample files (Damumed-shaped), built from the seeded DB on the fly."""
    builder = _SAMPLE_BUILDERS.get(filename)
    if builder is None:
        raise HTTPException(status_code=404, detail="unknown sample")
    return xlsx_response(builder(db), filename)


@router.get("/{file_id}/quarantine", response_model=QuarantineOut)
def get_quarantine(file_id: uuid.UUID, db: DbDep) -> QuarantineOut:
    """Rows rejected during import with per-row error lists."""
    if db.get(ImportFile, file_id) is None:
        raise HTTPException(status_code=404, detail="import file not found")
    rows = db.execute(
        sa.select(QuarantineRow)
        .where(QuarantineRow.import_file_id == file_id)
        .order_by(QuarantineRow.row_no)
    ).scalars()
    return QuarantineOut(
        file_id=file_id,
        rows=[QuarantineRowOut.model_validate(r) for r in rows],
    )
