"""Request schemas for the document-generation endpoints (docs/04 ACT, P7′)."""

from typing import Literal

from app.schemas.common import APIModel

Lang = Literal["kk", "ru"]


class ObrashenieIn(APIModel):
    """«Обращение в Фонд о размещении доп. объёмов» (пп. 25)/26) п. 19)."""

    line_key: str
    lang: Lang = "ru"


class VozrazhenieIn(APIModel):
    """Возражение по потенциальному дефекту (п. 26 — 5 раб. дней)."""

    case_ref: str
    lang: Lang = "ru"


class MonthlyReportIn(APIModel):
    year: int
    month: int
    lang: Lang = "kk"
