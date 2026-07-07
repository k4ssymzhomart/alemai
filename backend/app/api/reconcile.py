"""Reconciliation endpoints (docs/05 §5, buckets X1-X4 per docs/06 §7)."""

from typing import Annotated

from fastapi import APIRouter, Path

from app.api.deps import FiltersDep
from app.schemas.reconcile import BucketOut, BucketRowsOut, BucketsOut

router = APIRouter(prefix="/reconcile", tags=["reconcile"])

_BUCKET_DEFS: list[tuple[str, str, str]] = [
    ("X1", "Көрсетілген, бірақ шот қойылмаған", "Оказано, но не выставлено"),
    ("X2", "Шот қойылған, бірақ МАЖ-да жоқ", "Выставлено, но нет в МИС"),
    ("X3", "Қабылданған, бірақ төленбеген (>45 күн)", "Принято, но не оплачено (>45 дн.)"),
    ("X4", "Сома сәйкес емес (МАЖ ↔ портал)", "Расхождение сумм (МИС ↔ портал)"),
]


@router.get("/buckets", response_model=BucketsOut)
def get_buckets(filters: FiltersDep) -> BucketsOut:
    """Four discrepancy buckets with ₸ totals. Stub: zeroed buckets."""
    return BucketsOut(
        buckets=[
            BucketOut(
                bucket_no=i,
                code=code,
                title_kk=title_kk,
                title_ru=title_ru,
                rows_count=0,
                total_amount=0,
            )
            for i, (code, title_kk, title_ru) in enumerate(_BUCKET_DEFS, start=1)
        ]
    )


@router.get("/bucket/{bucket_no}/rows", response_model=BucketRowsOut)
def get_bucket_rows(bucket_no: Annotated[int, Path(ge=1, le=4)]) -> BucketRowsOut:
    """Claim-level drill-down for one bucket."""
    return BucketRowsOut(bucket_no=bucket_no, rows=[])
