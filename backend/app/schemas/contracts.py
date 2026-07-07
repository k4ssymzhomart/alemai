"""Contracts API schemas (docs/05 §5)."""

import datetime
import uuid

from pydantic import Field

from app.models.enums import CareType, ContractStatus, FundingSource
from app.schemas.common import APIModel


class ContractOut(APIModel):
    id: uuid.UUID
    org_id: uuid.UUID
    year: int
    number: str
    status: ContractStatus


class ContractLineOut(APIModel):
    id: uuid.UUID
    contract_id: uuid.UUID
    care_type: CareType
    funding_source: FundingSource
    service_group: str | None = None
    month: str = Field(description="YYYY-MM")
    plan_qty: int
    plan_amount: int = Field(description="whole tenge")
    version_id: uuid.UUID


class ContractLinesOut(APIModel):
    contract_id: uuid.UUID
    as_of: datetime.date | None = None
    lines: list[ContractLineOut] = []


class AmendmentLineIn(APIModel):
    care_type: CareType
    funding_source: FundingSource
    service_group: str | None = None
    month: str = Field(description="YYYY-MM")
    plan_qty: int
    plan_amount: int = Field(description="whole tenge")


class AmendmentIn(APIModel):
    amendment_no: int
    effective_date: datetime.date
    note: str | None = None
    lines: list[AmendmentLineIn] = []


class AmendmentOut(APIModel):
    id: uuid.UUID
    contract_id: uuid.UUID
    amendment_no: int
    effective_date: datetime.date
    note: str | None = None
