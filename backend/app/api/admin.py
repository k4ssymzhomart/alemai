"""Admin endpoints (docs/05 §5): demo reset, thresholds (real, persisted)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import OptionalPrincipal
from app.db import get_db
from app.schemas.admin import DemoResetResult, ThresholdsIn, ThresholdsOut
from app.services import events as events_svc
from app.services.config import THRESHOLDS_KEY, get_thresholds, set_config

router = APIRouter(prefix="/admin", tags=["admin"])

DbDep = Annotated[Session, Depends(get_db)]


@router.post("/demo-reset", response_model=DemoResetResult, status_code=202)
def demo_reset() -> DemoResetResult:
    """Restore the seeded snapshot (<60s target). Stub: `make demo-reset` is the
    real path (re-seed); this endpoint is a placeholder."""
    return DemoResetResult(
        status="ok",
        restored_from_snapshot=False,
        duration_ms=0,
        note="use `make demo-reset` (full re-seed)",
    )


@router.get("/thresholds", response_model=ThresholdsOut)
def read_thresholds(db: DbDep) -> ThresholdsOut:
    """Current risk thresholds (persisted in app_config; defaults if unset)."""
    return ThresholdsOut(**get_thresholds(db))


@router.put("/thresholds", response_model=ThresholdsOut)
def update_thresholds(
    body: ThresholdsIn, db: DbDep, principal: OptionalPrincipal
) -> ThresholdsOut:
    """Persist risk thresholds and emit a threshold_changed event (realtime feed)."""
    before = get_thresholds(db)
    values = body.model_dump()
    set_config(db, THRESHOLDS_KEY, values)
    changes = {k: {"from": before.get(k), "to": v} for k, v in values.items()
               if before.get(k) != v}
    if changes:
        events_svc.threshold_changed(db, principal, changes=changes)
    db.commit()
    return ThresholdsOut(**values)
