"""Contracts, amendment versions and plan lines (docs/05 §4, A2 versioning)."""

import datetime
import uuid

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import CareType, ContractStatus, FundingSource, text_enum


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    year: Mapped[int] = mapped_column(Integer)
    number: Mapped[str] = mapped_column(String(64))
    status: Mapped[ContractStatus] = mapped_column(
        text_enum(ContractStatus), default=ContractStatus.active
    )

    versions: Mapped[list["ContractVersion"]] = relationship(back_populates="contract")
    lines: Mapped[list["ContractLine"]] = relationship(back_populates="contract")


class ContractVersion(Base):
    """A2: every доп.соглашение creates a version; lines reference the version."""

    __tablename__ = "contract_versions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contracts.id"), index=True)
    amendment_no: Mapped[int] = mapped_column(Integer, default=0)
    effective_date: Mapped[datetime.date] = mapped_column(Date)
    note: Mapped[str | None] = mapped_column(Text)

    contract: Mapped[Contract] = relationship(back_populates="versions")


class ContractLine(Base):
    """Plan line: care_type x funding_source x service_group x month."""

    __tablename__ = "contract_lines"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contracts.id"), index=True)
    care_type: Mapped[CareType] = mapped_column(text_enum(CareType))
    funding_source: Mapped[FundingSource] = mapped_column(text_enum(FundingSource))
    service_group: Mapped[str | None] = mapped_column(String(128))
    month: Mapped[str] = mapped_column(String(7))  # YYYY-MM
    plan_qty: Mapped[int] = mapped_column(Integer)
    plan_amount: Mapped[int] = mapped_column(BigInteger)  # whole tenge
    version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contract_versions.id"), index=True)

    contract: Mapped[Contract] = relationship(back_populates="lines")
    version: Mapped[ContractVersion] = relationship()
