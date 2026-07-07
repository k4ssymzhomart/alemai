"""Validate shared/i18n/ui_strings.csv (UI translation content authored by the i18n track).

Contract: CSV with header key,kk,ru,en; every REQUIRED_KEYS entry present; no empty
cells; keys are dot-namespaced lowercase; kk must not simply duplicate ru (except a
small allowlist of terms identical in both languages). LEAD converts this file into
frontend/locales/*.json — juniors never touch frontend/.

Exit 0 with "OK: ..." on success, exit 0 with "SKIP: ..." if the file does not exist
yet, exit 1 with one line per error otherwise.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parents[2] / "shared" / "i18n" / "ui_strings.csv"
KEY_RE = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)+$")
KK_EQ_RU_ALLOWED = {"funding.gobmp", "funding.osms", "common.plan"}

REQUIRED_KEYS = [
    "overview.title", "overview.kpi.execution_ytd", "overview.kpi.forecast_gap",
    "overview.kpi.risk_count", "overview.kpi.removed_mtd",
    "overview.table.line", "overview.table.care_type", "overview.table.source",
    "overview.table.plan", "overview.table.fact", "overview.table.forecast",
    "overview.table.execution_pct", "overview.table.risk", "overview.table.burn_out_date",
    "risk.title", "risk.class.critical_under", "risk.class.under", "risk.class.on_track",
    "risk.class.over", "risk.class.critical_over",
    "risk.card.deadline", "risk.card.protect_amount", "risk.card.generate_doc",
    "risk.card.postpone", "risk.card.not_relevant",
    "prebilling.title", "prebilling.run_check", "prebilling.verdict", "prebilling.positions",
    "prebilling.at_risk", "prebilling.severity", "prebilling.rule",
    "prebilling.export_exceptions", "prebilling.exclude_from_registry",
    "reconcile.title", "reconcile.bucket.rendered_not_billed", "reconcile.bucket.billed_not_in_mis",
    "reconcile.bucket.accepted_not_paid", "reconcile.bucket.amount_mismatch",
    "anomalies.title", "anomalies.requires_review", "anomalies.evidence",
    "anomalies.doctor_day_volume", "anomalies.template_packages", "anomalies.weekend_services",
    "calendar.title", "alerts.title", "alerts.severity.info", "alerts.severity.warning",
    "alerts.severity.critical",
    "copilot.title", "copilot.placeholder", "copilot.ask", "copilot.thinking",
    "copilot.sources", "copilot.show_calculation", "copilot.out_of_scope",
    "reports.title", "reports.monthly_report", "reports.generate", "reports.download",
    "reports.language",
    "city.title", "city.clinic", "city.risk_score", "city.rank",
    "admin.title", "admin.imports", "admin.rules", "admin.mappings", "admin.upload_file",
    "admin.rows_ok", "admin.rows_quarantined",
    "severity.block", "severity.warn", "severity.info",
    "common.plan", "common.fact", "common.deviation", "common.total", "common.month",
    "common.year", "common.period", "common.source", "common.save", "common.cancel",
    "common.search", "common.filter", "common.export", "common.loading", "common.error",
    "common.no_data",
    "funding.gobmp", "funding.osms",
    "care_type.pmsp", "care_type.kdu", "care_type.day_hosp", "care_type.hosp",
    "care_type.dent", "care_type.screening", "care_type.ambulance",
]


def main() -> int:
    if not CSV_PATH.exists():
        print("SKIP: ui_strings.csv not found yet")
        return 0

    errors: list[str] = []
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != ["key", "kk", "ru", "en"]:
            print(f"ERROR: header must be exactly key,kk,ru,en — got {reader.fieldnames}")
            return 1
        rows = list(reader)

    seen: dict[str, dict[str, str]] = {}
    for lineno, row in enumerate(rows, start=2):
        key = (row.get("key") or "").strip()
        if not key:
            errors.append(f"line {lineno}: empty key")
            continue
        if not KEY_RE.fullmatch(key):
            errors.append(f"line {lineno}: key {key!r} is not dot-namespaced lowercase")
        if key in seen:
            errors.append(f"line {lineno}: duplicate key {key!r}")
        seen[key] = row
        for col in ("kk", "ru", "en"):
            if not (row.get(col) or "").strip():
                errors.append(f"line {lineno} ({key}): empty {col} cell")
        kk, ru = (row.get("kk") or "").strip(), (row.get("ru") or "").strip()
        if kk and ru and kk == ru and key not in KK_EQ_RU_ALLOWED:
            errors.append(f"line {lineno} ({key}): kk is identical to ru — translate it")

    missing = [k for k in REQUIRED_KEYS if k not in seen]
    if missing:
        errors.append(f"missing {len(missing)} required keys: {', '.join(missing[:12])}"
                      + (" …" if len(missing) > 12 else ""))

    if errors:
        print("\n".join(errors))
        return 1
    print(f"OK: {len(seen)} ui strings ({len(REQUIRED_KEYS)} required keys covered)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
