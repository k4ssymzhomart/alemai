"""Admin API schemas (docs/05 §5, H5 demo reset; G thresholds)."""

from pydantic import Field

from app.schemas.common import APIModel


class DemoResetResult(APIModel):
    status: str = "ok"
    restored_from_snapshot: bool = False
    duration_ms: int = 0
    note: str | None = None


class ThresholdsIn(APIModel):
    under_pct: int = Field(ge=0, le=200)
    over_pct: int = Field(ge=0, le=300)
    burnout_days: int = Field(ge=1, le=365)
    materiality_tenge: int = Field(ge=0)


class ThresholdsOut(ThresholdsIn):
    pass
