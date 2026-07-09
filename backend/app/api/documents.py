"""Document generation endpoints (docs/04 ACT, P7′) — return .docx bytes.

Every number in a generated document is pulled from the DB at build time
(services/docgen/*), never from an LLM. kk strings carry a NEEDS-NATIVE-REVIEW
footer until the lead's review.
"""

import io
from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.documents import MonthlyReportIn, ObrashenieIn, VozrazhenieIn
from app.services.docgen import monthly_report, obrashenie, vozrazhenie
from app.services.docgen.data import LineNotFoundError
from app.services.docgen.vozrazhenie import CaseNotFoundError

router = APIRouter(prefix="/documents", tags=["documents"])

DbDep = Annotated[Session, Depends(get_db)]

DOCX_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


def _docx_response(data: bytes, filename: str) -> StreamingResponse:
    """Wrap docx bytes with the download headers (RFC 5987 filename*)."""
    return StreamingResponse(
        io.BytesIO(data),
        media_type=DOCX_MEDIA_TYPE,
        headers={
            "Content-Disposition": (
                f"attachment; filename=\"{filename}\"; "
                f"filename*=UTF-8''{quote(filename)}"
            )
        },
    )


@router.post("/obrashenie")
def generate_obrashenie(body: ObrashenieIn, db: DbDep) -> StreamingResponse:
    """«Обращение в Фонд о размещении доп. объёмов (пп. 25)/26) п. 19)»."""
    try:
        data = obrashenie.build(db, body.line_key, body.lang)
    except LineNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _docx_response(data, f"obrashenie_{body.lang}.docx")


@router.post("/vozrazhenie")
def generate_vozrazhenie(body: VozrazhenieIn) -> StreamingResponse:
    """Возражение по потенциальному дефекту (п. 26 Правил мониторинга)."""
    try:
        data = vozrazhenie.build(body.case_ref, body.lang)
    except CaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _docx_response(data, f"vozrazhenie_{body.case_ref}_{body.lang}.docx")


@router.post("/monthly-report")
def generate_monthly_report(body: MonthlyReportIn, db: DbDep) -> StreamingResponse:
    """Ай сайынғы басқару есебі / monthly management report."""
    data = monthly_report.build(db, body.year, body.month, body.lang)
    return _docx_response(
        data, f"report_{body.year}-{body.month:02d}_{body.lang}.docx"
    )
