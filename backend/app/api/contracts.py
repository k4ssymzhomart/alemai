"""Contracts endpoints (docs/05 §5). Stubs return typed empty shapes."""

import datetime
import uuid
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import FiltersDep
from app.schemas.contracts import AmendmentIn, AmendmentOut, ContractLinesOut, ContractOut

router = APIRouter(prefix="/contracts", tags=["contracts"])

AsOfQuery = Annotated[
    datetime.date | None, Query(description="A2 versioning: lines active as of this date")
]


@router.get("", response_model=list[ContractOut])
def list_contracts(filters: FiltersDep) -> list[ContractOut]:
    """List contracts. Stub: empty until ingest lands."""
    return []


@router.get("/{contract_id}/lines", response_model=ContractLinesOut)
def get_contract_lines(contract_id: uuid.UUID, as_of: AsOfQuery = None) -> ContractLinesOut:
    """Plan lines of the contract version active as of the given date."""
    return ContractLinesOut(contract_id=contract_id, as_of=as_of, lines=[])


@router.post("/{contract_id}/amendments", response_model=AmendmentOut, status_code=201)
def create_amendment(contract_id: uuid.UUID, body: AmendmentIn) -> AmendmentOut:
    """Register a доп.соглашение as a new contract version (A2). Stub: echo shape."""
    return AmendmentOut(
        id=uuid.uuid4(),
        contract_id=contract_id,
        amendment_no=body.amendment_no,
        effective_date=body.effective_date,
        note=body.note,
    )
