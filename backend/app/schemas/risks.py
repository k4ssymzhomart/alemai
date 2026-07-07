"""Risk register API schemas (docs/05 §5, D2/D5, recommendations docs/06 §9)."""

import datetime
import uuid
from typing import Literal

from pydantic import Field

from app.models.enums import RiskClass
from app.schemas.common import APIModel, LineKey


class RiskOut(APIModel):
    id: uuid.UUID
    line_key: LineKey
    as_of: datetime.date
    risk_class: RiskClass
    gap_amount: int = Field(default=0, description="whole tenge, signed")
    burn_out_date: datetime.date | None = None


class RisksOut(APIModel):
    risks: list[RiskOut] = []


class RecommendationOut(APIModel):
    """Risk -> action mapping (docs/06 §9): action, tenge impact, deadline."""

    risk_id: uuid.UUID
    action_type: str = Field(
        description="zayavka_increase | zayavka_decrease | reallocation | capacity | campaign"
    )
    impact_amount: int = Field(default=0, description="whole tenge")
    deadline: datetime.date | None = None
    text_kk: str = ""
    text_ru: str = ""
    artifact_available: bool = False


class GenerateDocIn(APIModel):
    lang: Literal["kk", "ru"] = "kk"


class DocGenResult(APIModel):
    """Stub result until docgen service produces real .docx files."""

    filename: str
    content_type: str = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    status: str = "stub"
    note: str | None = None
