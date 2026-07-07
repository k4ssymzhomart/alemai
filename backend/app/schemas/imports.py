"""Imports API schemas (docs/05 §5)."""

import uuid
from typing import Any

from app.models.enums import ImportKind
from app.schemas.common import APIModel


class ImportResult(APIModel):
    file_id: uuid.UUID
    kind: ImportKind
    filename: str
    rows_ok: int = 0
    quarantined: int = 0


class QuarantineRowOut(APIModel):
    row_no: int
    raw: dict[str, Any]
    errors: list[str]


class QuarantineOut(APIModel):
    file_id: uuid.UUID
    rows: list[QuarantineRowOut] = []
