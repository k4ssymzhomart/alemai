"""Reconciliation — money finders, not defects (docs/06 §7 [СВЕРКА], B3).

Four buckets over claim ``status``, each with a ₸ total and claim-level
drill-down. Bucket 1 (оказано-но-не-выставлено) is the recoverable money the
storyline plants (mis_only). Totals are read straight from ``claims`` — no
invented numbers.

  1  mis_only            — оказано (МИС), но не выставлено в счёт-реестр
  2  rejected            — выставлено, но снято (отклонено Фондом)
  3  accepted+submitted  — принято/на рассмотрении, но не оплачено (aging)
  4  paid                — совпадает (оплачено)
"""

from __future__ import annotations

import datetime
import uuid
from dataclasses import dataclass

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.models.claim import Claim

# bucket_no -> (statuses, code, title_kk, title_ru)
_BUCKETS: dict[int, tuple[tuple[str, ...], str, str, str]] = {
    1: (("mis_only",), "X1",
        "Көрсетілген, бірақ шот қойылмаған",
        "Оказано, но не выставлено"),
    2: (("rejected",), "X2",
        "Шот қойылған, бірақ алынып тасталды",
        "Выставлено, но снято"),
    3: (("accepted", "submitted"), "X3",
        "Қабылданған, бірақ төленбеген",
        "Принято, но не оплачено"),
    4: (("paid",), "X4",
        "Сәйкес келеді (төленген)",
        "Совпадает (оплачено)"),
}


@dataclass(frozen=True, slots=True)
class BucketTotal:
    bucket_no: int
    code: str
    title_kk: str
    title_ru: str
    rows_count: int
    total_amount: int


@dataclass(frozen=True, slots=True)
class ReconcileRow:
    claim_id: uuid.UUID
    patient_id: str
    service_code: str
    service_name: str
    date_start: datetime.date
    amount: int
    detail: str


def buckets(session: Session) -> list[BucketTotal]:
    """All four buckets with ₸ totals and counts, computed from ``claims``."""
    counts: dict[str, int] = {}
    amounts: dict[str, int] = {}
    for status, n, amount in session.execute(
        sa.select(
            Claim.status,
            sa.func.count(),
            sa.func.coalesce(sa.func.sum(Claim.amount), 0),
        ).group_by(Claim.status)
    ).all():
        counts[str(status)] = int(n)
        amounts[str(status)] = int(amount)

    result: list[BucketTotal] = []
    for bucket_no, (statuses, code, title_kk, title_ru) in _BUCKETS.items():
        result.append(
            BucketTotal(
                bucket_no=bucket_no,
                code=code,
                title_kk=title_kk,
                title_ru=title_ru,
                rows_count=sum(counts.get(s, 0) for s in statuses),
                total_amount=sum(amounts.get(s, 0) for s in statuses),
            )
        )
    return result


def bucket_rows(session: Session, bucket_no: int, limit: int = 200) -> list[ReconcileRow]:
    """Claim-level drill-down for one bucket (largest ₸ first)."""
    statuses = _BUCKETS[bucket_no][0]
    title_ru = _BUCKETS[bucket_no][3]
    rows = session.execute(
        sa.select(
            Claim.id, Claim.patient_id, Claim.service_code, Claim.service_name,
            Claim.date_start, Claim.amount,
        )
        .where(Claim.status.in_(statuses))
        .order_by(Claim.amount.desc(), Claim.id)
        .limit(limit)
    ).all()
    return [
        ReconcileRow(
            claim_id=r.id,
            patient_id=r.patient_id,
            service_code=r.service_code,
            service_name=r.service_name,
            date_start=r.date_start,
            amount=int(r.amount),
            detail=title_ru,
        )
        for r in rows
    ]
