"""Anomalies — doctor-workload outliers computed straight from claims (H2).

Two cheap detectors over the seeded data (same signals as rules R10/R11):
day-volume outliers (≥ N claims for one doctor on one day) and weekend-service
outliers (≥ N weekend claims for one doctor in a month). Neutral framing —
«требует проверки», never an accusation (docs/11 standing law). Curator is
scoped out (doctor-level detail).
"""

from typing import Annotated

import sqlalchemy as sa
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import DenyCurator
from app.db import get_db
from app.models.claim import Claim
from app.models.people import Doctor
from app.schemas.anomalies import AnomaliesOut, AnomalyOut

router = APIRouter(prefix="/anomalies", tags=["anomalies"])

DbDep = Annotated[Session, Depends(get_db)]

DAY_VOLUME_THRESHOLD = 60  # claims by one doctor in a single day
WEEKEND_THRESHOLD = 20  # weekend claims by one doctor in a month


@router.get("", response_model=AnomaliesOut, dependencies=[DenyCurator])
def list_anomalies(
    db: DbDep, limit: Annotated[int, Query(ge=1, le=100)] = 30
) -> AnomaliesOut:
    """Doctor-workload outliers, most extreme first. Curator: 403 (doctor-level)."""
    doctors = {str(d.id): d for d in db.execute(sa.select(Doctor)).scalars()}

    def _who(doctor_id: object) -> Doctor | None:
        return doctors.get(str(doctor_id))

    items: list[AnomalyOut] = []

    for row in db.execute(
        sa.select(Claim.doctor_id, Claim.date_start, sa.func.count().label("n"))
        .group_by(Claim.doctor_id, Claim.date_start)
        .having(sa.func.count() >= DAY_VOLUME_THRESHOLD)
        .order_by(sa.func.count().desc())
        .limit(limit)
    ):
        d = _who(row.doctor_id)
        items.append(AnomalyOut(
            type="day_volume", doctor=d.full_name_masked if d else "—",
            specialty=d.specialty if d else "—", dept=d.dept if d else "—",
            period=row.date_start.isoformat(), count=int(row.n),
            threshold=DAY_VOLUME_THRESHOLD,
        ))

    dow = sa.func.extract("dow", Claim.date_start)
    for row in db.execute(
        sa.select(Claim.doctor_id, Claim.period, sa.func.count().label("n"))
        .where(dow.in_([0, 6]))
        .group_by(Claim.doctor_id, Claim.period)
        .having(sa.func.count() >= WEEKEND_THRESHOLD)
        .order_by(sa.func.count().desc())
        .limit(limit)
    ):
        d = _who(row.doctor_id)
        items.append(AnomalyOut(
            type="weekend", doctor=d.full_name_masked if d else "—",
            specialty=d.specialty if d else "—", dept=d.dept if d else "—",
            period=str(row.period), count=int(row.n), threshold=WEEKEND_THRESHOLD,
        ))

    items.sort(key=lambda a: a.count, reverse=True)
    return AnomaliesOut(
        items=items[:limit],
        day_volume_threshold=DAY_VOLUME_THRESHOLD,
        weekend_threshold=WEEKEND_THRESHOLD,
    )
