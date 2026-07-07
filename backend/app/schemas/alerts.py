"""Alerts & deadlines API schemas (docs/05 §5, F1)."""

import datetime
import uuid

from pydantic import Field

from app.models.enums import AlertSeverity, AlertStatus, DeadlineKind
from app.schemas.common import APIModel


class AlertOut(APIModel):
    id: uuid.UUID
    type: str
    severity: AlertSeverity
    title_kk: str
    title_ru: str
    amount: int | None = Field(default=None, description="whole tenge")
    due_date: datetime.date | None = None
    entity_ref: str | None = None
    status: AlertStatus = AlertStatus.active


class AlertsOut(APIModel):
    alerts: list[AlertOut] = []


class DeadlineOut(APIModel):
    id: uuid.UUID
    kind: DeadlineKind
    starts: datetime.date
    ends: datetime.date
    note: str | None = None


class DeadlinesOut(APIModel):
    deadlines: list[DeadlineOut] = []
