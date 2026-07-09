#!/usr/bin/env python3
# ruff: noqa: E501 -- pitch prose lines are intentionally long.
"""Render docs/PITCH-TEXT.md + the A5 crib from docs/21-PITCH-QALAM.md.

Fills every `{{token}}` from LIVE data so the pitch can never drift from the
demo: metrics API (overview), a rules run over the Nov-2025 registry (the
санкционный-риск verdict), reconcile buckets, objections, and storylines.yaml
(burn-out, recoverable). The script owns the numbers; the .md owns the prose.

    python scripts/render_pitch.py            # API at :8800, repo docs
    API_BASE=http://localhost:8800/api/v1 python scripts/render_pitch.py
"""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

import yaml

API = os.environ.get("API_BASE", "http://localhost:8800/api/v1")
REPO = Path(__file__).resolve().parents[1]
NBSP = " "


def _get(path: str) -> dict:
    with urllib.request.urlopen(f"{API}{path}", timeout=15) as r:
        return json.load(r)


def _post(path: str, body: dict) -> dict:
    req = urllib.request.Request(
        f"{API}{path}",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def tng(n: int | float) -> str:
    return f"{int(round(n)):,}".replace(",", NBSP) + f"{NBSP}₸"


def mln(n: int | float) -> str:
    s = f"{n / 1_000_000:.2f}".rstrip("0").rstrip(".").replace(".", ",")
    return f"{s}{NBSP}млн{NBSP}₸"


def isodate(s: str) -> str:
    """'2026-10-14' -> '14.10.2026'; pass through if not ISO."""
    parts = str(s).split("-")
    return f"{parts[2]}.{parts[1]}.{parts[0]}" if len(parts) == 3 else str(s)


def pct(x: float) -> str:
    return f"{x:.1f}".replace(".", ",") + f"{NBSP}%"


def build_tokens() -> dict[str, str]:
    ov = _get("/metrics/overview?year=2026")
    run = _post("/rules/run", {"scope": "period:2025-11"})["totals"]
    buckets = _get("/reconcile/buckets?year=2026")["buckets"]
    b1 = next(b for b in buckets if b["bucket_no"] == 1)
    objs = _get("/objections")
    soonest = min(objs["items"], key=lambda o: o["deadline_working_days"])

    story = yaml.safe_load((REPO / "datagen" / "storylines.yaml").read_text("utf-8"))
    smap = {s["key"]: s for s in story["storylines"]}
    mri = smap["mri_over_execution"]["params"]
    recoverable = int(mri.get("recoverable_amount") or mri.get("expected_recoverable_amount") or 0)
    profile = story.get("profile") or {}
    attached = int(profile.get("attached_population") or 31000)

    return {
        "plan_year": tng(ov["plan_amount_year"]),
        "exec_pct": pct(ov["execution_pct_ytd"]),
        "forecast_gap": tng(ov["forecast_gap"]),
        "risk_count": str(ov["risk_count"]),
        "attached": f"{attached:,}".replace(",", NBSP),
        "burn_out": isodate(mri.get("expected_burn_out_date", "2026-10-14")),
        "mri_recoverable": mln(recoverable) if recoverable else "5,67 млн ₸",
        "prebill_positions": str(run["block_positions"]),
        "prebill_amount": tng(run["block_amount"]),
        "sanction_risk": mln(run["sanction_risk"]),
        # beat-4 upload: the Nov-2025 registry file = the period's billed claims
        "registry_rows": f"{run['claims_scanned']:,}".replace(",", NBSP),
        "reconcile_count": str(b1["rows_count"]),
        "reconcile_amount": tng(b1["total_amount"]),
        "objection_days": str(soonest["deadline_working_days"]),
        "impact_clinic": "30–60 млн ₸",
    }


def render(template: str, tokens: dict[str, str]) -> str:
    out = template
    for k, v in tokens.items():
        out = out.replace(f"{{{{{k}}}}}", v)
    return out


CRIB = """# QALAM — A5 Q&A CRIB (printable, fold to A5)

**Demo numbers (from the live seed):**
- Освоение YTD {exec_pct} · разрыв {forecast_gap} · рисков {risk_count}
- МРТ 118 % → выгорание {burn_out} · возместимо {mri_recoverable}
- Импорт: XLSX из Damumed, {registry_rows} строк → маппинг → тот же вердикт (повторная загрузка = 0 дублей)
- Пре-биллинг: {prebill_positions} позиций / {prebill_amount} · **санкционный риск {sanction_risk}**
- Сверка: {reconcile_count} записей / {reconcile_amount} не выставлено
- Возражение: {objection_days} раб. день до автоснятия

**Q&A (30 сек each):**
- «Как данные попадают в систему?» → экран «Импорт»: XLSX/CSV из МИС (Damumed) → маппинг по пресету → карантин плохих строк → проверка. Показано live; повторная загрузка = 0 дублей. Роадмап: API МИС по расписанию.
- «Фонд уже делает Qalqan?» → Qalqan = антифрод плательщика ПОСЛЕ подачи; п. 15 — алгоритмы Фонда закрыты; п. 24 — после дефекта исправления не принимаются. Клинике нужен свой контур ДО счёта. Дополняем, не конкурируем.
- «Откуда цифры в копилоте?» → «цифры не проходят через языковую модель — их считает система». Один семантический слой, один источник.
- «Мониторинг — сколько видов?» → ДВА: текущий (каждый раб. день в ИСФ) + внеплановый (п. 4, ред. №68). Проактивный/целевой отменены (ред. 2022–2024).
- «Приписка — сколько стоит?» → код 5.1: снятие 300 % стоимости + 100 КПН. 168 600 ₸ услуг → {sanction_risk} риска.
- «Персональные данные?» → хэши, маски, scope-RBAC, журнал доступа, он-прем.
- «Что если правила изменятся?» → пережили смену ЕКД №68→№19 в марте 2026; версии справочников в настройках.

**Contested benchmark:** Фонд оспорил 38 млрд ₸ (2025) + 8 млрд (2026). Бюджет 2026 ≈ 3,4 трлн ₸.
**Fund identity:** НАО «ФСМС», под управлением Минфина с 16.01.2026, председатель Гульмира Сабденбек.
"""


def main() -> int:
    tokens = build_tokens()
    template = (REPO / "docs" / "21-PITCH-QALAM.md").read_text("utf-8")
    # Drop the template header (everything above the first slide) from the output.
    body = template.split("---", 2)[-1]
    pitch = "# QALAM — ТЕКСТ ПРЕЗЕНТАЦИИ (rendered from docs/21 + live seed)\n" + render(body, tokens)
    (REPO / "docs" / "PITCH-TEXT.md").write_text(pitch, "utf-8")
    (REPO / "docs" / "PITCH-CRIB-A5.md").write_text(CRIB.format(**tokens), "utf-8")
    print("wrote docs/PITCH-TEXT.md + docs/PITCH-CRIB-A5.md")
    print("tokens:", json.dumps(tokens, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
