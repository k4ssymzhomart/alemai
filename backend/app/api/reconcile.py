"""Reconciliation endpoints (docs/05 §5, buckets X1-X4 per docs/06 §7)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.reconcile import BucketOut, BucketRowsOut, BucketsOut, ReconcileRowOut
from app.services import reconcile as svc

router = APIRouter(prefix="/reconcile", tags=["reconcile"])

DbDep = Annotated[Session, Depends(get_db)]


@router.get("/buckets", response_model=BucketsOut)
def get_buckets(db: DbDep) -> BucketsOut:
    """Four discrepancy buckets with ₸ totals + counts (computed from claims)."""
    return BucketsOut(
        buckets=[
            BucketOut(
                bucket_no=b.bucket_no,
                code=b.code,
                title_kk=b.title_kk,
                title_ru=b.title_ru,
                rows_count=b.rows_count,
                total_amount=b.total_amount,
            )
            for b in svc.buckets(db)
        ]
    )


@router.get("/bucket/{bucket_no}/rows", response_model=BucketRowsOut)
def get_bucket_rows(
    db: DbDep,
    bucket_no: Annotated[int, Path(ge=1, le=4)],
    limit: Annotated[int, Query(ge=1, le=2000)] = 200,
) -> BucketRowsOut:
    """Claim-level drill-down for one bucket (largest ₸ first)."""
    return BucketRowsOut(
        bucket_no=bucket_no,
        rows=[
            ReconcileRowOut(
                claim_id=r.claim_id,
                patient_id=r.patient_id,
                service_code=r.service_code,
                service_name=r.service_name,
                date_start=r.date_start,
                amount=r.amount,
                detail=r.detail,
            )
            for r in svc.bucket_rows(db, bucket_no, limit)
        ],
    )
