"""Shared schema primitives."""

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    """Base for all response/request bodies; ORM-friendly."""

    model_config = ConfigDict(from_attributes=True)


class StatusOut(APIModel):
    status: str = "ok"
    note: str | None = None


class LineKey(APIModel):
    """Composite line identity used by metrics/forecasts/risks (docs/05 §4)."""

    contract_id: str
    care_type: str
    funding_source: str
    service_group: str | None = None


class ListFilters(APIModel):
    """Common list filters (docs/05 §5: contract, source, care_type, period)."""

    contract: str | None = None
    source: str | None = None
    care_type: str | None = None
    period: str | None = Field(default=None, description="YYYY-MM")
