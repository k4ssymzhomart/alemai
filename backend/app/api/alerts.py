"""Alerts and deadline calendar endpoints (docs/05 §5, F1)."""

from fastapi import APIRouter

from app.api.deps import FiltersDep
from app.schemas.alerts import AlertsOut, DeadlinesOut

router = APIRouter(tags=["alerts"])


@router.get("/alerts", response_model=AlertsOut)
def list_alerts(filters: FiltersDep) -> AlertsOut:
    """Alert feed: new risks, burn-out <45d, windows, deadlines, снятия."""
    return AlertsOut(alerts=[])


@router.get("/deadlines", response_model=DeadlinesOut)
def list_deadlines() -> DeadlinesOut:
    """Deadline calendar (корректировка windows, invoices, reports)."""
    return DeadlinesOut(deadlines=[])
