"""Report generation endpoint (docs/05 §5, G4)."""

from fastapi import APIRouter

from app.schemas.reports import MonthlyReportIn
from app.schemas.risks import DocGenResult

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/monthly", response_model=DocGenResult, status_code=202)
def generate_monthly_report(body: MonthlyReportIn) -> DocGenResult:
    """Monthly management report docx/pdf. Stub: filename convention only."""
    content_type = (
        "application/pdf"
        if body.fmt == "pdf"
        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    return DocGenResult(
        filename=f"report_{body.month}_{body.lang}.{body.fmt}",
        content_type=content_type,
        status="stub",
        note="docgen service not implemented yet",
    )
