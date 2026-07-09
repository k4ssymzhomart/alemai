"""Domain-event writers (EPIC G2) — one terse helper per event type.

Each helper composes a bilingual title + severity + a deep link and adds an
``Event`` to the caller's session (committed in the same transaction as the
mutation it describes). ``actor``/``role`` come from the request principal when
present; system-initiated events fall back to «Жүйе».
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.events import Event
from app.services.auth import Principal


def _tenge(n: int) -> str:
    return f"{int(n):,}".replace(",", " ") + " ₸"


def record_event(
    db: Session,
    *,
    type: str,
    title_ru: str,
    title_kk: str,
    severity: str = "info",
    principal: Principal | None = None,
    entity_ref: str | None = None,
    link: str | None = None,
    payload: dict[str, Any] | None = None,
) -> Event:
    event = Event(
        type=type,
        severity=severity,
        actor=principal.name if principal and principal.name else "Жүйе",
        actor_username=principal.username if principal else None,
        role=principal.role if principal else None,
        entity_ref=entity_ref,
        link=link,
        title_ru=title_ru,
        title_kk=title_kk,
        payload=payload,
    )
    db.add(event)
    return event


# ---------------------------------------------------------------------------
# typed writers (one per event type in the lead's spec)
# ---------------------------------------------------------------------------

def finding_status_changed(
    db: Session, principal: Principal | None, *, finding_id: str, rule_code: str,
    ekd_code: str | None, amount: int, status: str,
) -> Event:
    excluded = status == "excluded"
    etype = "finding_excluded" if excluded else "finding_dismissed"
    ru_verb = "исключена из счёт-реестра" if excluded else "снята с рассмотрения"
    kk_verb = "шот-тізілімнен алынып тасталды" if excluded else "қараудан алынды"
    code = ekd_code or rule_code
    return record_event(
        db, type=etype, severity="info", principal=principal,
        entity_ref=f"finding:{finding_id}", link="/prebilling",
        title_ru=f"Позиция {ru_verb} · {code} · {_tenge(amount)}",
        title_kk=f"Позиция {kk_verb} · {code} · {_tenge(amount)}",
        payload={"rule_code": rule_code, "ekd_code": ekd_code, "amount": amount},
    )


def rules_run_finished(
    db: Session, principal: Principal | None, *, scope: str, totals: dict[str, Any],
    triggered_by: str = "manual",
) -> Event:
    positions = int(totals.get("block_positions", 0))
    amount = int(totals.get("block_amount", 0))
    sev = "warn" if positions else "info"
    return record_event(
        db, type="rules_run_finished", severity=sev, principal=principal,
        entity_ref=f"run:{scope}", link="/prebilling",
        title_ru=f"Проверка реестра ({scope}): {positions} позиций · {_tenge(amount)}",
        title_kk=f"Тізілім тексерілді ({scope}): {positions} позиция · {_tenge(amount)}",
        payload={"scope": scope, "triggered_by": triggered_by,
                 "block_positions": positions, "block_amount": amount,
                 "sanction_risk": int(totals.get("sanction_risk", 0))},
    )


def import_completed(
    db: Session, principal: Principal | None, *, filename: str, period: str | None,
    rows_ok: int, quarantined: int, new: int, matched: int,
) -> Event:
    sev = "warn" if quarantined else "info"
    per = period or "—"
    return record_event(
        db, type="import_completed", severity=sev, principal=principal,
        entity_ref=f"import:{filename}", link="/imports",
        title_ru=f"Импорт {filename} ({per}): {rows_ok} строк, карантин {quarantined}",
        title_kk=f"Импорт {filename} ({per}): {rows_ok} жол, карантин {quarantined}",
        payload={"filename": filename, "period": period, "rows_ok": rows_ok,
                 "quarantined": quarantined, "new": new, "matched": matched},
    )


def document_generated(
    db: Session, principal: Principal | None, *, kind: str, ru_label: str,
    kk_label: str, lang: str, link: str, entity: str,
) -> Event:
    return record_event(
        db, type="document_generated", severity="info", principal=principal,
        entity_ref=entity, link=link,
        title_ru=f"Сформирован документ: {ru_label} ({lang})",
        title_kk=f"Құжат жасалды: {kk_label} ({lang})",
        payload={"kind": kind, "lang": lang},
    )


def objection_filed(
    db: Session, principal: Principal | None, *, case_ref: str, lang: str,
) -> Event:
    return record_event(
        db, type="objection_filed", severity="warn", principal=principal,
        entity_ref=f"objection:{case_ref}", link="/prebilling",
        title_ru=f"Возражение сформировано по случаю {case_ref}",
        title_kk=f"{case_ref} жағдайы бойынша қарсылық жасалды",
        payload={"case_ref": case_ref, "lang": lang},
    )


def threshold_changed(
    db: Session, principal: Principal | None, *, changes: dict[str, Any],
) -> Event:
    return record_event(
        db, type="threshold_changed", severity="info", principal=principal,
        entity_ref="settings:thresholds", link="/admin",
        title_ru="Пороги рисков изменены",
        title_kk="Тәуекел шектері өзгертілді",
        payload={"changes": changes},
    )
