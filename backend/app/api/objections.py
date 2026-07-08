"""Возражения / DF-timers endpoint (storyline 8 — feeds the DF-лента + DeadlineBox)."""

from typing import Annotated

from fastapi import APIRouter, Query

from app.schemas.objections import ObjectionOut, ObjectionsOut
from app.services.rules_engine import objections

router = APIRouter(tags=["objections"])

DemoTodayQuery = Annotated[
    str | None, Query(description="override demo anchor YYYY-MM-DD (default: storylines.yaml)")
]


@router.get("/objections", response_model=ObjectionsOut)
def get_objections(demo_today: DemoTodayQuery = None) -> ObjectionsOut:
    """Four потенциальных дефекта with concrete objection deadlines (working days)."""
    today, items = objections.list_objections(demo_today)
    out = [
        ObjectionOut(
            case_ref=o.case_ref,
            ekd_code=o.ekd_code,
            ekd_name_ru=o.ekd_name_ru,
            ekd_name_kk=o.ekd_name_kk,
            significance=o.significance,
            yellow=o.yellow,
            amount_at_stake=o.amount_at_stake,
            deadline_working_days=o.deadline_working_days,
            deadline_date=o.deadline_date,
        )
        for o in items
    ]
    return ObjectionsOut(
        demo_today=today,
        defect_count=len(out),
        total_amount_at_stake=sum(o.amount_at_stake for o in out),
        items=out,
    )
