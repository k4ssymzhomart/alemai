"""Copilot API schemas (docs/05 §5-§6, docs/07)."""

from typing import Any, Literal

from pydantic import Field

from app.schemas.common import APIModel


class CopilotAskIn(APIModel):
    question: str
    locale: Literal["kk", "ru", "en"] = "kk"
    screen_context: str | None = Field(
        default=None, description="which screen the user asked from, e.g. 'overview'"
    )


class CitationOut(APIModel):
    """Rendered by the UI as «п. X, приказ Y» (docs/05 §6)."""

    doc_title: str
    doc_number: str
    anchor: str
    lang: str = "kk"


class ToolTraceOut(APIModel):
    tool: str
    arguments: dict[str, Any] = {}
    result_preview: str | None = None


class CopilotAnswerOut(APIModel):
    """Plain JSON stub for now; SSE streaming later per docs/05 §5."""

    answer: str
    intent: Literal["data", "regulation", "report", "out_of_scope"] = "out_of_scope"
    locale: str = "kk"
    citations: list[CitationOut] = []
    tool_traces: list[ToolTraceOut] = []
