"""Alerts and deadline calendar endpoints (docs/05 §5, F1; H2 fill-or-kill)."""

from typing import Annotated

import sqlalchemy as sa
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import FiltersDep
from app.db import get_db
from app.models.alerts import Deadline
from app.schemas.alerts import AlertsOut, DeadlineOut, DeadlinesOut

router = APIRouter(tags=["alerts"])

DbDep = Annotated[Session, Depends(get_db)]


@router.get("/alerts", response_model=AlertsOut)
def list_alerts(filters: FiltersDep) -> AlertsOut:
    """Alert feed: new risks, burn-out <45d, windows, deadlines, снятия."""
    return AlertsOut(alerts=[])


@router.get("/deadlines", response_model=DeadlinesOut)
def list_deadlines(db: DbDep) -> DeadlinesOut:
    """Seeded regulatory deadline calendar (ordered by end date) — H2 Календарь."""
    rows = db.execute(sa.select(Deadline).order_by(Deadline.ends)).scalars()
    return DeadlinesOut(deadlines=[DeadlineOut.model_validate(d) for d in rows])
