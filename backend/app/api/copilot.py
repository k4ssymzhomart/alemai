"""Copilot endpoint (docs/05 §5-§6, docs/07). Plain JSON stub; SSE later."""

from fastapi import APIRouter

from app.schemas.copilot import CopilotAnswerOut, CopilotAskIn

router = APIRouter(prefix="/copilot", tags=["copilot"])

_STUB_ANSWERS = {
    "kk": (
        "Көмекші әзірге іске қосылмаған. Мен үш нәрсеге жауап бере аламын: "
        "деректер бойынша сұрақтар, нормативтік құжаттар және есеп жобалары."
    ),
    "ru": (
        "Копилот пока не подключен. Я умею три вещи: вопросы по данным, "
        "вопросы по нормативке и черновики отчётов."
    ),
    "en": (
        "The copilot is not wired up yet. It will support three capabilities: "
        "data Q&A, regulations Q&A with citations, and report drafting."
    ),
}


@router.post("/ask", response_model=CopilotAnswerOut)
def ask(body: CopilotAskIn) -> CopilotAnswerOut:
    """Answer a question. Stub: fixed out-of-scope reply, no LLM call, no numbers."""
    return CopilotAnswerOut(
        answer=_STUB_ANSWERS.get(body.locale, _STUB_ANSWERS["kk"]),
        intent="out_of_scope",
        locale=body.locale,
        citations=[],
        tool_traces=[],
    )
