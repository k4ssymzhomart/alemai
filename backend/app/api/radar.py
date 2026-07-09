"""Normative radar endpoints (EPIC G5) — «Дереккөз тексерісі»."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import OptionalPrincipal
from app.db import get_db
from app.models.events import RadarCheck
from app.schemas.radar import RadarCheckResult, RadarOut, RadarRowOut
from app.services import radar as radar_svc

router = APIRouter(prefix="/radar", tags=["radar"])

DbDep = Annotated[Session, Depends(get_db)]


def _rows(db: Session) -> list[RadarRowOut]:
    checks = radar_svc.get_rows(db)
    out: list[RadarRowOut] = []
    for src in radar_svc.RADAR_SOURCES:
        row = checks.get(src.id)
        out.append(RadarRowOut(
            source_id=src.id, name_ru=src.name_ru, name_kk=src.name_kk,
            our_version=row.our_version if row else src.our_version,
            detected_version=row.detected_version if row else None,
            status=row.status if row else "manual",
            message=row.message if row else None,
            checked_at=row.checked_at if row else None,
            official_url=src.official_url, mirror_url=src.mirror_url,
            quick_link=src.quick_link, fetchable=src.fetchable,
        ))
    return out


@router.get("", response_model=RadarOut)
def get_radar(db: DbDep) -> RadarOut:
    """The source registry with each source's latest check status."""
    rows = _rows(db)
    return RadarOut(rows=rows, checked_any=any(r.checked_at for r in rows))


@router.post("/check", response_model=RadarCheckResult)
def run_check(db: DbDep, principal: OptionalPrincipal) -> RadarCheckResult:
    """«Тексеру» — live-fetch every mirror, compare versions, emit events."""
    summary = radar_svc.run_checks(db, principal)
    return RadarCheckResult(summary=summary, rows=_rows(db))


@router.get("/provider-status")
def provider_status() -> dict:
    """ФСМС healthcare-subjects registry status for the org-header badge (H0.4).

    Live reachability check; degrades to a quick-link when offline. No DB, no auth
    — it's a public registry lookup surfaced as a trust badge.
    """
    return radar_svc.check_provider_registry()


@router.post("/{source_id}/confirm", response_model=RadarRowOut)
def confirm_source(source_id: str, db: DbDep) -> RadarRowOut:
    """«Отметить обновлённым» — accept the detected edition as ours (no auto-apply)."""
    if source_id not in radar_svc.SOURCE_BY_ID:
        raise HTTPException(status_code=404, detail="unknown source")
    row: RadarCheck | None = radar_svc.confirm(db, source_id)
    if row is None:
        raise HTTPException(status_code=404, detail="source not checked yet")
    src = radar_svc.SOURCE_BY_ID[source_id]
    return RadarRowOut(
        source_id=src.id, name_ru=src.name_ru, name_kk=src.name_kk,
        our_version=row.our_version, detected_version=row.detected_version,
        status=row.status, message=row.message, checked_at=row.checked_at,
        official_url=src.official_url, mirror_url=src.mirror_url,
        quick_link=src.quick_link, fetchable=src.fetchable,
    )
