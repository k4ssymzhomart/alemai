"""Admin API schemas (docs/05 §5, H5 demo reset)."""

from app.schemas.common import APIModel


class DemoResetResult(APIModel):
    status: str = "ok"
    restored_from_snapshot: bool = False
    duration_ms: int = 0
    note: str | None = None
