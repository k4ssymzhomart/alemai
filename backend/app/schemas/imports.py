"""Imports API schemas (docs/05 §5, EPIC F1/F3)."""

import uuid
from typing import Any

from app.schemas.common import APIModel


class ColumnMapOut(APIModel):
    """Auto-map report entry: file column → system field (None = ignored)."""

    column: str
    field: str | None = None
    status: str  # auto | ignored | unknown
    confidence: str | None = None  # CONFIRMED | LIKELY | INFERRED (docs/research)
    note: str | None = None


class QuarantineRowOut(APIModel):
    row_no: int
    raw: dict[str, Any]
    errors: list[str]


class QuarantineOut(APIModel):
    file_id: uuid.UUID
    rows: list[QuarantineRowOut] = []


class RegistryImportOut(APIModel):
    """POST /imports/mis-registry result — feeds the 3-step Импорт reveal."""

    file_id: uuid.UUID
    filename: str
    preset: str
    period_detected: str | None
    rows_total: int
    rows_ok: int
    matched: int
    updated: int
    new: int
    quarantined: int
    control_sum: int
    claims_in_period: int
    mapping: list[ColumnMapOut]
    quarantine: list[QuarantineRowOut]
    rule_run_id: uuid.UUID | None = None
    rule_totals: dict[str, Any] | None = None


class AnnexLineDiffOut(APIModel):
    """One annex line in the «Доп. соглашение — предпросмотр» diff (F3)."""

    care_type: str
    funding_source: str
    service_group: str
    plan_current: int
    plan_annex: int
    delta: int
    status: str  # changed | unchanged | new | missing


class AnnexPreviewOut(APIModel):
    filename: str
    year: int
    lines: list[AnnexLineDiffOut]
    changed: int
    total_current: int
    total_annex: int
    total_delta: int
    preview_only: bool = True
