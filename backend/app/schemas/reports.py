"""Reports API schemas (docs/05 §5, G4)."""

from typing import Literal

from pydantic import Field

from app.schemas.common import APIModel


class MonthlyReportIn(APIModel):
    month: str = Field(description="YYYY-MM")
    lang: Literal["kk", "ru"] = "kk"
    fmt: Literal["docx", "pdf"] = "docx"
