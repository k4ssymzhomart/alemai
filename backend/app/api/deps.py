"""Shared FastAPI dependencies for the /api/v1 routers."""

from typing import Annotated

from fastapi import Depends, Query

from app.schemas.common import ListFilters

PeriodQuery = Annotated[str | None, Query(description="YYYY-MM")]


def list_filters(
    contract: str | None = None,
    source: str | None = None,
    care_type: str | None = None,
    period: PeriodQuery = None,
) -> ListFilters:
    """Common list filters (docs/05 §5): contract, source, care_type, period."""
    return ListFilters(contract=contract, source=source, care_type=care_type, period=period)


FiltersDep = Annotated[ListFilters, Depends(list_filters)]
