"""Risk register endpoints (docs/05 §5, D2/D5, docs/06 §9)."""

import datetime
import uuid

from fastapi import APIRouter

from app.api.deps import FiltersDep
from app.schemas.risks import DocGenResult, GenerateDocIn, RecommendationOut, RisksOut

router = APIRouter(prefix="/risks", tags=["risks"])


@router.get("", response_model=RisksOut)
def list_risks(filters: FiltersDep) -> RisksOut:
    """Risk register ranked by tenge at stake. Stub: empty."""
    return RisksOut(risks=[])


@router.get("/{risk_id}/recommendation", response_model=RecommendationOut)
def get_recommendation(risk_id: uuid.UUID) -> RecommendationOut:
    """Rule-based recommendation card for one risk (docs/06 §9)."""
    return RecommendationOut(
        risk_id=risk_id,
        action_type="zayavka_increase",
        impact_amount=0,
        deadline=None,
        text_kk="",
        text_ru="",
        artifact_available=False,
    )


@router.post("/{risk_id}/generate-doc", response_model=DocGenResult, status_code=202)
def generate_doc(risk_id: uuid.UUID, body: GenerateDocIn) -> DocGenResult:
    """Generate заявка docx (docs/04 ACT). Stub: returns filename convention only."""
    today = datetime.date.today().isoformat()
    return DocGenResult(
        filename=f"zayavka_korrektirovka_{today}.docx",
        status="stub",
        note=f"docgen service not implemented yet (risk {risk_id}, lang={body.lang})",
    )
