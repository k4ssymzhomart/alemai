"""Admin endpoints (docs/05 §5, H5 demo reset)."""

from fastapi import APIRouter

from app.schemas.admin import DemoResetResult

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/demo-reset", response_model=DemoResetResult, status_code=202)
def demo_reset() -> DemoResetResult:
    """Restore the seeded pg_dump snapshot (<60s target). Stub: no-op."""
    return DemoResetResult(
        status="ok",
        restored_from_snapshot=False,
        duration_ms=0,
        note="snapshot restore not implemented yet",
    )
