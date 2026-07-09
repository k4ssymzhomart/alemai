"""Normative radar API schemas (EPIC G5)."""

import datetime

from app.schemas.common import APIModel


class RadarRowOut(APIModel):
    source_id: str
    name_ru: str
    name_kk: str
    our_version: str
    detected_version: str | None = None
    status: str  # ok | stale | unreachable | manual
    message: str | None = None
    checked_at: datetime.datetime | None = None
    official_url: str
    mirror_url: str | None = None
    quick_link: str
    fetchable: bool


class RadarOut(APIModel):
    rows: list[RadarRowOut]
    checked_any: bool = False


class RadarCheckResult(APIModel):
    summary: dict[str, int]
    rows: list[RadarRowOut]
