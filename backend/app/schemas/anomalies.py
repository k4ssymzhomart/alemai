"""Anomalies API schemas (H2) — neutral language, «требует проверки»."""

from app.schemas.common import APIModel


class AnomalyOut(APIModel):
    type: str  # day_volume | weekend
    doctor: str  # masked name
    specialty: str
    dept: str
    period: str  # ISO date (day_volume) or YYYY-MM (weekend)
    count: int
    threshold: int


class AnomaliesOut(APIModel):
    items: list[AnomalyOut] = []
    day_volume_threshold: int = 0
    weekend_threshold: int = 0
