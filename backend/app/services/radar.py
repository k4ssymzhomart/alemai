"""Нормативный радар (EPIC G5) — validate our stored reference versions against
official sources.

Primary sources (adilet.zan.kz) block bots, so the radar fetches the Эталонный
банк НПА mirror (zakon.uchet.kz) and extracts the «с изменениями на: DD.MM.YYYY»
marker (docs/research/official_sources.csv). Everything degrades gracefully: an
unreachable source (offline venue) shows «недоступен — открыть вручную» + a
quick link. No auto-apply — a newer edition surfaces «Отметить обновлённым»
(manual confirm); PDF-diffing is roadmap.
"""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass

import httpx
import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.models.events import RadarCheck
from app.services.auth import Principal

# Universal ru+kk marker (newline-agnostic; the decoy «Дата обновления:» above it
# is not matched). official_sources.csv §0.
VERSION_RE = re.compile(r"(?:Обновленный\s+)?с изменениями на:\s*(\d{2}\.\d{2}\.\d{4})")
_FETCH_TIMEOUT = 8.0


@dataclass(frozen=True, slots=True)
class RadarSource:
    id: str
    name_ru: str
    name_kk: str
    our_version: str
    observed_version: str | None  # last-audited official version (2026-07-09)
    official_url: str
    mirror_url: str | None
    quick_link: str
    fetchable: bool


# Curated from docs/research/official_sources.csv (CONFIRMED fetchable rows).
# NB: `tarif` intentionally ships one edition behind observed → demonstrates the
# «⚠ доступна новее» state without needing the fetch to disagree.
RADAR_SOURCES: tuple[RadarSource, ...] = (
    RadarSource(
        "monitoring", "Правила мониторинга + ЕКД (прил. 1)",
        "Мониторинг қағидалары + БЖС",
        "27.02.2026", "27.02.2026",
        "https://adilet.zan.kz/rus/docs/V2000021904",
        "https://zakon.uchet.kz/rus/docs/V2000021904",
        "https://adilet.zan.kz/rus/docs/V2000021904", True,
    ),
    RadarSource(
        "zakup", "Правила закупа услуг", "Сатып алу қағидалары",
        "05.01.2026", "05.01.2026",
        "https://adilet.zan.kz/rus/docs/V2000021744",
        "https://zakon.uchet.kz/rus/docs/V2000021744",
        "https://adilet.zan.kz/rus/docs/V2000021744", True,
    ),
    RadarSource(
        "oplata", "Правила оплаты услуг", "Ақы төлеу қағидалары",
        "18.05.2026", "18.05.2026",
        "https://adilet.zan.kz/rus/docs/V2000021831",
        "https://zakon.uchet.kz/rus/docs/V2000021831",
        "https://adilet.zan.kz/rus/docs/V2000021831", True,
    ),
    RadarSource(
        "tarif", "Тарификатор (ДСМ-170/2020, прил. 7)", "Тарификатор (ДСМ-170/2020)",
        "12.11.2025", "31.12.2025",  # our version deliberately behind → ⚠
        "https://adilet.zan.kz/rus/docs/V2000021550",
        "https://zakon.uchet.kz/rus/docs/V2000021550",
        "https://prg.kz/document/?doc_id=36534682", True,
    ),
    RadarSource(
        "gobmp672", "Перечень ГОБМП (ПП № 672)", "ТМККК тізбесі (Қ № 672)",
        "01.01.2026", "01.01.2026",
        "https://adilet.zan.kz/rus/docs/P2000000672",
        "https://zakon.uchet.kz/rus/docs/P2000000672",
        "https://adilet.zan.kz/rus/docs/P2000000672", True,
    ),
    RadarSource(
        "osms421", "Перечень ОСМС (ПП № 421)", "МӘМС тізбесі (Қ № 421)",
        "01.01.2026", "01.01.2026",
        "https://adilet.zan.kz/rus/docs/P1900000421",
        "https://zakon.uchet.kz/rus/docs/P1900000421",
        "https://adilet.zan.kz/rus/docs/P1900000421", True,
    ),
    RadarSource(
        "mrp_kpn", "МРП / КПН (подушевой норматив)", "АЕК / ЖБШН",
        "3 932 ₸ (2025) · КПН 1710", None,
        "https://adilet.zan.kz/rus/docs/V2000021550",
        None,
        "https://adilet.zan.kz/rus/docs/V2000021550", False,  # no clean machine marker
    ),
)
SOURCE_BY_ID: dict[str, RadarSource] = {s.id: s for s in RADAR_SOURCES}


def _status_for(our: str, detected: str | None, *, fetchable: bool) -> str:
    if not fetchable:
        return "manual"
    if detected is None:
        return "unreachable"
    return "ok" if detected == our else "stale"


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


# ---------------------------------------------------------------------------
# live fetch
# ---------------------------------------------------------------------------

def _fetch_version(url: str) -> str | None:
    try:
        resp = httpx.get(url, timeout=_FETCH_TIMEOUT, follow_redirects=True,
                         headers={"User-Agent": "Mozilla/5.0 QalamRadar"})
        resp.raise_for_status()
    except (httpx.HTTPError, httpx.InvalidURL):
        return None
    match = VERSION_RE.search(resp.text)
    return match.group(1) if match else None


def run_checks(db: Session, principal: Principal | None) -> dict[str, int]:
    """Live-check every source; upsert radar_checks; emit an event per stale one."""
    from app.services import events as events_svc  # local: avoid import cycle

    summary = {"ok": 0, "stale": 0, "unreachable": 0, "manual": 0}
    for src in RADAR_SOURCES:
        detected = _fetch_version(src.mirror_url) if (src.fetchable and src.mirror_url) else None
        status = _status_for(src.our_version, detected, fetchable=src.fetchable)
        summary[status] = summary.get(status, 0) + 1
        message = {
            "ok": "актуально",
            "stale": f"доступна новее: {detected}",
            "unreachable": "источник недоступен — открыть вручную",
            "manual": "проверка вручную по ссылке",
        }[status]
        _upsert(db, src.id, status, src.our_version, detected, message)
        if status == "stale":
            events_svc.record_event(
                db, type="source_update_available", severity="warn", principal=principal,
                entity_ref=f"radar:{src.id}", link="/admin",
                title_ru=f"Норматив обновлён: {src.name_ru} → {detected}",
                title_kk=f"Норматив жаңарды: {src.name_kk} → {detected}",
                payload={"source_id": src.id, "detected": detected},
            )
    db.commit()
    return summary


def confirm(db: Session, source_id: str) -> RadarCheck | None:
    """«Отметить обновлённым» — accept the detected version as ours (manual)."""
    row = db.get(RadarCheck, source_id)
    if row is None:
        return None
    if row.detected_version:
        row.our_version = row.detected_version
    row.status = "ok"
    row.message = "отмечено обновлённым вручную"
    row.checked_at = _now()
    db.commit()
    return row


def _upsert(db: Session, source_id: str, status: str, our: str,
            detected: str | None, message: str) -> None:
    row = db.get(RadarCheck, source_id)
    if row is None:
        db.add(RadarCheck(
            source_id=source_id, checked_at=_now(), status=status,
            our_version=our, detected_version=detected, message=message,
        ))
    else:
        row.status = status
        row.detected_version = detected
        row.message = message
        row.checked_at = _now()


def get_rows(db: Session) -> dict[str, RadarCheck]:
    return {r.source_id: r for r in db.execute(sa.select(RadarCheck)).scalars()}


_MESSAGES = {
    "ok": "актуально",
    "stale": "доступна новее",
    "unreachable": "источник недоступен — открыть вручную",
    "manual": "проверка вручную по ссылке",
}


def seed_initial(connection: sa.Connection) -> int:
    """Seed radar_checks from the last-audited official versions (EPIC G5) so the
    demo shows ✓/⚠/— offline. A live «Тексеру» re-fetches and overwrites."""
    for src in RADAR_SOURCES:
        detected = src.observed_version if src.fetchable else None
        status = _status_for(src.our_version, detected, fetchable=src.fetchable)
        message = _MESSAGES[status] + (f": {detected}" if status == "stale" else "")
        connection.execute(
            sa.text(
                "INSERT INTO radar_checks "
                "(source_id, checked_at, status, our_version, detected_version, message) "
                "VALUES (:sid, now(), :st, :our, :det, :msg) "
                "ON CONFLICT (source_id) DO UPDATE SET checked_at=now(), status=:st, "
                "our_version=:our, detected_version=:det, message=:msg"
            ),
            {"sid": src.id, "st": status, "our": src.our_version,
             "det": detected, "msg": message},
        )
    return len(RADAR_SOURCES)
