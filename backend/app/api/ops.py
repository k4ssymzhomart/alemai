"""Ops dashboard endpoint (EPIC G4) — live counters for «Операциялық панель»."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.ops import CounterOut, OpsDashboardOut, RefVersionOut
from app.services import ops as ops_svc

router = APIRouter(prefix="/ops", tags=["ops"])

DbDep = Annotated[Session, Depends(get_db)]


@router.get("/dashboard", response_model=OpsDashboardOut)
def get_dashboard(db: DbDep) -> OpsDashboardOut:
    d = ops_svc.dashboard(db)
    return OpsDashboardOut(
        registries_checked=d.registries_checked,
        positions_scanned=d.positions_scanned,
        findings_total=d.findings_total,
        findings_by_severity=[CounterOut(key=c.key, count=c.count) for c in d.findings_by_severity],
        sanctions_prevented_tenge=d.sanctions_prevented_tenge,
        objections_filed=d.objections_filed,
        documents_generated=d.documents_generated,
        documents_by_kind=[CounterOut(key=c.key, count=c.count) for c in d.documents_by_kind],
        reconcile_cases=d.reconcile_cases,
        reconcile_tenge=d.reconcile_tenge,
        imports_count=d.imports_count,
        import_rows_ok=d.import_rows_ok,
        import_rows_quarantined=d.import_rows_quarantined,
        active_users=d.active_users,
        events_total=d.events_total,
        last_demo_reset=d.last_demo_reset,
        app_version=d.app_version,
        ref_versions=[RefVersionOut(**r) for r in d.ref_versions],
    )
