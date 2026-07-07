"""Reconciliation API schemas (docs/05 §5, buckets X1-X4 docs/06 §7)."""

import datetime
import uuid

from pydantic import Field

from app.schemas.common import APIModel


class BucketOut(APIModel):
    bucket_no: int = Field(ge=1, le=4)
    code: str = Field(description="X1..X4")
    title_kk: str
    title_ru: str
    rows_count: int = 0
    total_amount: int = Field(default=0, description="whole tenge")


class BucketsOut(APIModel):
    buckets: list[BucketOut] = []


class ReconcileRowOut(APIModel):
    claim_id: uuid.UUID | None = None
    patient_id: str | None = None
    service_code: str | None = None
    service_name: str | None = None
    date_start: datetime.date | None = None
    amount: int = Field(default=0, description="whole tenge")
    detail: str | None = None


class BucketRowsOut(APIModel):
    bucket_no: int
    rows: list[ReconcileRowOut] = []
