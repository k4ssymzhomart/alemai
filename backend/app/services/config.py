"""app_config accessors (EPIC G) — a tiny key→JSON store for thresholds and
demo-reset bookkeeping. No dedicated settings tables."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.events import AppConfig

# Risk thresholds surfaced in Settings (docs/13 §3): under/over-execution %,
# burn-out horizon (days), materiality (₸).
THRESHOLDS_KEY = "thresholds"
DEFAULT_THRESHOLDS: dict[str, int] = {
    "under_pct": 90,
    "over_pct": 105,
    "burnout_days": 45,
    "materiality_tenge": 100_000,
}
LAST_DEMO_RESET_KEY = "last_demo_reset"


def get_config(db: Session, key: str, default: dict[str, Any]) -> dict[str, Any]:
    row = db.get(AppConfig, key)
    return dict(row.value) if row is not None else dict(default)


def set_config(db: Session, key: str, value: dict[str, Any]) -> None:
    row = db.get(AppConfig, key)
    if row is None:
        db.add(AppConfig(key=key, value=value))
    else:
        row.value = value


def get_thresholds(db: Session) -> dict[str, int]:
    return {**DEFAULT_THRESHOLDS, **get_config(db, THRESHOLDS_KEY, DEFAULT_THRESHOLDS)}
