"""Возражения / DF-timers — storyline-8 potential defects with objection windows.

Serves the four потенциальных дефекта from ``datagen/storylines.yaml`` (CONFIRMED
ЕКД codes + amounts) with concrete objection deadlines. Правила мониторинга
(ҚР ДСМ-321/2020, пп. 26-27): возражение подаётся в рабочих днях, молчание =
автоснятие. Deadlines are computed from ``demo_today`` skipping Sat/Sun (KZ
holidays ignored — same rule as the datagen working-day helper).

Source of truth is ``storylines.yaml`` (resolved from $DATAGEN_DIR, /datagen, or
the repo checkout); a small embedded copy is the last-resort fallback so the API
never 500s if the file is absent. Amounts are the ЕКД sanction (e.g. 300 % for
5.1) as planted — not recomputed here.
"""

from __future__ import annotations

import datetime
import os
from dataclasses import dataclass
from pathlib import Path

import yaml

from app.services.rules_engine import ekd

_BACKEND_DIR = Path(__file__).resolve().parents[3]
_REPO_DIR = _BACKEND_DIR.parent

# Last-resort fallback (mirrors datagen/storylines.yaml storyline 8, CONFIRMED).
_FALLBACK_DEMO_TODAY = "2026-07-09"
_FALLBACK_DEFECTS: list[dict[str, object]] = [
    {"case_ref": "IGR-2026-000114-1", "ekd_code": "5.1",
     "ekd_name_ru": "Включение в счёт-реестр неподтверждённого случая (снятие 300%)",
     "amount_at_stake": 55500, "deadline_working_days": 1},
    {"case_ref": "IGR-2026-000114-2", "ekd_code": "3.1",
     "ekd_name_ru": "Необоснованное увеличение количества услуг",
     "amount_at_stake": 8400, "deadline_working_days": 3},
    {"case_ref": "IGR-2026-000114-3", "ekd_code": "1.2",
     "ekd_name_ru": "Необоснованное направление/оказание КДУ",
     "amount_at_stake": 3400, "deadline_working_days": 4},
    {"case_ref": "IGR-2026-000114-4", "ekd_code": "2.0",
     "ekd_name_ru": "Дефекты оформления меддокументации (незначительное, 0 ₸, фиксируется)",
     "amount_at_stake": 0, "deadline_working_days": 5},
]


@dataclass(frozen=True, slots=True)
class Objection:
    case_ref: str
    ekd_code: str
    ekd_name_ru: str
    ekd_name_kk: str
    significance: str
    yellow: bool
    amount_at_stake: int
    deadline_working_days: int
    deadline_date: datetime.date


def _add_working_days(start: datetime.date, n: int) -> datetime.date:
    """Date ``n`` working days after ``start`` (skip Sat/Sun) — matches datagen."""
    d = start
    remaining = n
    while remaining > 0:
        d += datetime.timedelta(days=1)
        if d.weekday() < 5:
            remaining -= 1
    return d


def _storylines_path() -> Path | None:
    for candidate in (
        os.environ.get("DATAGEN_DIR"),
        "/datagen",
        str(_REPO_DIR / "datagen"),
    ):
        if not candidate:
            continue
        path = Path(candidate) / "storylines.yaml"
        if path.exists():
            return path
    return None


def _load_story8() -> tuple[str, list[dict[str, object]]]:
    """Return (demo_today, defects) from storylines.yaml, else the fallback."""
    path = _storylines_path()
    if path is not None:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        demo_today = str(data.get("demo_today", _FALLBACK_DEMO_TODAY))
        for story in data.get("storylines", []):
            if story.get("key") == "objection_window":
                defects = story.get("defects") or []
                if defects:
                    return demo_today, defects
    return _FALLBACK_DEMO_TODAY, _FALLBACK_DEFECTS


def list_objections(demo_today: str | None = None) -> tuple[datetime.date, list[Objection]]:
    """Resolve the four defects with concrete objection deadlines."""
    story_today, defects = _load_story8()
    today = datetime.date.fromisoformat(demo_today or story_today)
    items: list[Objection] = []
    for d in defects:
        code = str(d["ekd_code"])
        n = int(d["deadline_working_days"])
        try:
            meta = ekd.get(code)
            name_kk, significance, yellow = meta.name_kk, meta.significance, meta.yellow
        except KeyError:
            name_kk, significance, yellow = "", "значительное", False
        items.append(
            Objection(
                case_ref=str(d["case_ref"]),
                ekd_code=code,
                ekd_name_ru=str(d.get("ekd_name_ru", "")),
                ekd_name_kk=name_kk,
                significance=significance,
                yellow=yellow,
                amount_at_stake=int(d["amount_at_stake"]),
                deadline_working_days=n,
                deadline_date=_add_working_days(today, n),
            )
        )
    return today, items
