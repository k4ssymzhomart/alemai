"""Claims — the atomic service/case rows every pillar computes from (docs/05 §4)."""

import datetime
import uuid

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.enums import CareType, ClaimStatus, FundingSource, text_enum


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True)
    doctor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("doctors.id"), index=True)
    dept: Mapped[str] = mapped_column(String(128))
    care_type: Mapped[CareType] = mapped_column(text_enum(CareType), index=True)
    funding_source: Mapped[FundingSource] = mapped_column(text_enum(FundingSource), index=True)
    service_code: Mapped[str] = mapped_column(String(64), index=True)
    service_name: Mapped[str] = mapped_column(String(255))
    icd10: Mapped[str | None] = mapped_column(String(16))
    date_start: Mapped[datetime.date] = mapped_column(Date, index=True)
    date_end: Mapped[datetime.date | None] = mapped_column(Date)
    qty: Mapped[int] = mapped_column(Integer, default=1)
    tariff: Mapped[int] = mapped_column(BigInteger)  # whole tenge
    amount: Mapped[int] = mapped_column(BigInteger)  # whole tenge
    referral_id: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[ClaimStatus] = mapped_column(
        text_enum(ClaimStatus), default=ClaimStatus.mis_only, index=True
    )
    period: Mapped[str] = mapped_column(String(7), index=True)  # YYYY-MM
    source_file_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("import_files.id"))
