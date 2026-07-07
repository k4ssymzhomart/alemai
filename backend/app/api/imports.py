"""Imports endpoints (docs/05 §5). Stubs: accept upload, return typed shapes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from app.models.enums import ImportKind
from app.schemas.imports import ImportResult, QuarantineOut

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/{kind}", response_model=ImportResult, status_code=201)
async def upload_import(
    kind: ImportKind,
    file: Annotated[UploadFile, File(description="XLSX/CSV export")],
) -> ImportResult:
    """Accept an XLSX/CSV export; stub does not parse or persist yet."""
    return ImportResult(
        file_id=uuid.uuid4(),
        kind=kind,
        filename=file.filename or "upload",
        rows_ok=0,
        quarantined=0,
    )


@router.get("/{file_id}/quarantine", response_model=QuarantineOut)
def get_quarantine(file_id: uuid.UUID) -> QuarantineOut:
    """Rows rejected during import with per-row error lists."""
    return QuarantineOut(file_id=file_id, rows=[])
