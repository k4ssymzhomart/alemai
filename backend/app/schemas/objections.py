"""Возражения / DF-timers API schemas (storyline 8, docs/16 §1 C2/C3)."""

import datetime

from pydantic import Field

from app.schemas.common import APIModel


class ObjectionOut(APIModel):
    """One потенциальный дефект with its objection deadline (working-day timer)."""

    case_ref: str
    ekd_code: str = Field(description="real ЕКД code (docs/research/ekd_codes.csv)")
    ekd_name_ru: str
    ekd_name_kk: str = ""
    significance: str = Field(default="значительное", description="значительное|не значительное")
    yellow: bool = Field(default=False, description="ЕКД 2.0/7.0 — фиксируется без снятия")
    amount_at_stake: int = Field(default=0, description="whole tenge — ЕКД sanction (снятие)")
    deadline_working_days: int = Field(description="1/3/4/5 раб. дней (Правила мониторинга)")
    deadline_date: datetime.date = Field(description="concrete deadline, weekends skipped")


class ObjectionsOut(APIModel):
    demo_today: datetime.date
    defect_count: int = 0
    total_amount_at_stake: int = Field(default=0, description="whole tenge")
    items: list[ObjectionOut] = []
