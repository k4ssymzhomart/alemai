"""City panel endpoint (docs/05 §5, C5 curator view)."""

from fastapi import APIRouter

from app.schemas.city import CityOverviewOut

router = APIRouter(prefix="/city", tags=["city"])


@router.get("/overview", response_model=CityOverviewOut)
def city_overview() -> CityOverviewOut:
    """14 clinics ranked by composite risk; aggregates only, no patient level."""
    return CityOverviewOut(as_of=None, clinics=[])
