"""Copilot endpoint (docs/05 §5-§6, docs/07, docs/11 P8).

Numbers are computed by the semantic layer, never by an LLM — the pipeline
runs a deterministic keyword router + templates that work with the network off
(the mandatory canned mode).
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.copilot import CopilotAnswerOut, CopilotAskIn
from app.services.copilot import pipeline

router = APIRouter(prefix="/copilot", tags=["copilot"])

DbDep = Annotated[Session, Depends(get_db)]


@router.post("/ask", response_model=CopilotAnswerOut)
def ask(body: CopilotAskIn, db: DbDep) -> CopilotAnswerOut:
    """Answer a data/regulation/report question, or refuse out-of-scope ones."""
    return pipeline.answer(db, body.question, body.locale)
