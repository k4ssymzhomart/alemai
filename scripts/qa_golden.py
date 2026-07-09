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
# Auth bootstrap (EPIC G1): act as an admin service principal so the golden
# checks keep passing after routes read the session role. Header-based — no
# login round-trip.
SERVICE_TOKEN = os.environ.get("QALAM_SERVICE_TOKEN", "qalam-service-token-demo")
_AUTH = {"X-Service-Token": SERVICE_TOKEN}
_fails = 0


def get(path: str) -> dict:
    req = urllib.request.Request(f"{API}{path}", headers=_AUTH)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def post(path: str, body: dict) -> dict:
    req = urllib.request.Request(
        f"{API}{path}", data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", **_AUTH}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def get_bytes(path: str) -> bytes:
    req = urllib.request.Request(f"{API}{path}", headers=_AUTH)
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def post_multipart(path: str, filename: str, blob: bytes) -> dict:
    """Minimal stdlib multipart upload (one file field named 'file')."""
    boundary = "----qalam-qa-golden"
    body = (
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            "Content-Type: application/octet-stream\r\n\r\n"
        ).encode()
        + blob
        + f"\r\n--{boundary}--\r\n".encode()
    )
    req = urllib.request.Request(
        f"{API}{path}", data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}", **_AUTH},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as r:
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

    # EPIC F1 — the file-exchange beat: sample registry round-trip must leave
    # every golden number untouched, and a re-upload must change nothing (the
    # idempotency that makes a live demo upload safe).
    blob = get_bytes("/imports/samples/registry_2025-11.xlsx")
    check("import", "sample registry > 1 MB", len(blob) > 1_000_000, True)
    imp1 = post_multipart("/imports/mis-registry", "registry_2025-11.xlsx", blob)
    check("import", "rows_ok == rows_total", imp1["rows_ok"] == imp1["rows_total"], True)
    check("import", "quarantined", imp1["quarantined"], 0)
    check("import", "new", imp1["new"], 0)
    check("import", "updated", imp1["updated"], 0)
    check("import", "period_detected", imp1["period_detected"], "2025-11")
    t1 = imp1["rule_totals"]
    check("import", "verdict positions", t1["block_positions"], 46)
    check("import", "verdict amount", t1["block_amount"], 168600)
    check("import", "verdict sanction", t1["sanction_risk"], 6665700)

    imp2 = post_multipart("/imports/mis-registry", "registry_2025-11.xlsx", blob)
    check("import", "re-upload matched unchanged", imp2["matched"], imp1["matched"])
    check("import", "re-upload new", imp2["new"], 0)
    check("import", "re-upload claims_in_period",
          imp2["claims_in_period"], imp1["claims_in_period"])

    ov2 = get("/metrics/overview?year=2026")
    check("import", "overview gap unchanged", ov2["forecast_gap"], 70061600)
    b1b = next(b for b in get("/reconcile/buckets?year=2026")["buckets"]
               if b["bucket_no"] == 1)
    check("import", "bucket1 unchanged",
          (b1b["rows_count"], b1b["total_amount"]), (260, 2992000))

    print(f"\nQA GOLDEN: {'ALL PASS' if _fails == 0 else str(_fails) + ' FAIL'}")
    return 1 if _fails else 0


if __name__ == "__main__":
    sys.exit(main())
