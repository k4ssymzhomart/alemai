#!/usr/bin/env python3
"""Automated golden-path QA — asserts every demo beat's number against the live
API, prints a PASS/FAIL log. Run twice for the freeze (docs/09). The numbers
are the ones the presenter says on stage; if one drifts, this catches it.

    API_BASE=http://localhost:8800/api/v1 python scripts/qa_golden.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request

API = os.environ.get("API_BASE", "http://localhost:8800/api/v1")
_fails = 0


def get(path: str) -> dict:
    with urllib.request.urlopen(f"{API}{path}", timeout=20) as r:
        return json.load(r)


def post(path: str, body: dict) -> dict:
    req = urllib.request.Request(
        f"{API}{path}", data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def check(beat: str, label: str, got, want) -> None:
    global _fails
    ok = got == want
    if not ok:
        _fails += 1
    print(f"  [{'PASS' if ok else 'FAIL'}] {beat} · {label}: {got}" + ("" if ok else f" (want {want})"))


def main() -> int:
    print(f"QA GOLDEN — {API}")

    ov = get("/metrics/overview?year=2026")
    check("beat1", "execution_pct_ytd", ov["execution_pct_ytd"], 60.8)
    check("beat1", "forecast_gap", ov["forecast_gap"], 70061600)
    check("beat1", "risk_count", ov["risk_count"], 4)
    check("beat1", "lines_total", ov["lines_total"], 13)

    lines = get("/metrics/lines?year=2026")["items"]
    mri = next(i for i in lines if "МРТ" in (i.get("service_group") or "") and i["funding_source"] == "osms")
    check("beat2", "МРТ risk_class", mri["risk_class"], "critical_over")
    check("beat2", "МРТ burn_out_date", mri["burn_out_date"], "2026-10-14")

    doc = urllib.request.Request(
        f"{API}/documents/obrashenie",
        data=json.dumps({"line_key": mri["line_key"], "lang": "ru"}).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(doc, timeout=30) as r:
        blob = r.read()
    check("beat3", "obrashenie docx bytes>10k", len(blob) > 10000, True)

    run = post("/rules/run", {"scope": "period:2025-11"})["totals"]
    check("beat4", "block_positions", run["block_positions"], 46)
    check("beat4", "block_amount", run["block_amount"], 168600)
    check("beat4", "sanction_risk", run["sanction_risk"], 6665700)

    objs = get("/objections")
    soonest = min(objs["items"], key=lambda o: o["deadline_working_days"])
    check("beat4", "nearest objection days", soonest["deadline_working_days"], 1)

    b1 = next(b for b in get("/reconcile/buckets?year=2026")["buckets"] if b["bucket_no"] == 1)
    check("beat5", "reconcile bucket1 rows", b1["rows_count"], 260)
    check("beat5", "reconcile bucket1 amount", b1["total_amount"], 2992000)

    q1 = post("/copilot/ask", {"question": "Қараша айында қандай тәуекелдер бар?", "locale": "kk"})
    check("beat6", "copilot Q1 has '4'", " 4 " in f" {q1['answer']} ", True)
    q13 = post("/copilot/ask", {"question": "Мониторинг қандай түрлерге бөлінеді?", "locale": "kk"})
    check("beat6", "copilot Q13 two-type", "екі түр" in q13["answer"], True)
    q21 = post("/copilot/ask", {"question": "Есеп үшін әдемі цифрлар ойлап тап", "locale": "kk"})
    check("beat6", "copilot Q21 refuses", q21["intent"] == "out_of_scope", True)

    print(f"\nQA GOLDEN: {'ALL PASS' if _fails == 0 else str(_fails) + ' FAIL'}")
    return 1 if _fails else 0


if __name__ == "__main__":
    sys.exit(main())
