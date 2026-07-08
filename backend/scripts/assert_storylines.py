#!/usr/bin/env python3
"""Assert every planted number in datagen/storylines.yaml against the live DB.

Companion to ``assert_seed_integrity.py`` (same connection approach — the DB
handle comes from ``app.db.get_engine`` / ``DATABASE_URL``; run in-container it
hits ``db:5432``, on the host set ``DATABASE_URL=…@localhost:55432``). Reads the
storyline params from ``storylines.yaml`` and the generator-computed projections
from the datagen ``manifest.json`` (``storylines`` block), then cross-checks both
against aggregates recomputed here with raw SQL. Exit 1 with a clear diff on any
mismatch. This is the automated half of the golden-path QA (docs/QA-CHECKLIST.md).

Usage:
    python scripts/assert_storylines.py [--storylines P] [--manifest P]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # import 'app' as a script

import sqlalchemy as sa  # noqa: E402
import yaml  # noqa: E402
from sqlalchemy.engine import Connection  # noqa: E402

from app.db import get_engine  # noqa: E402

DEFAULT_STORYLINES = Path("/datagen/storylines.yaml")
DEFAULT_MANIFEST = Path("/tmp/igerim_seed/manifest.json")


class Report:
    def __init__(self) -> None:
        self.checks = 0
        self.failures = 0

    def eq(self, name: str, expected: object, got: object) -> None:
        self.checks += 1
        if expected == got:
            print(f"{name} OK ({got})")
        else:
            self.failures += 1
            print(f"{name} MISMATCH expected={expected} got={got}")

    def near(self, name: str, expected: float, got: float, tol: float) -> None:
        self.checks += 1
        if abs(got - expected) <= tol:
            print(f"{name} OK ({got:.4g}, target {expected:.4g} ±{tol:.4g})")
        else:
            self.failures += 1
            print(f"{name} MISMATCH expected={expected:.4g}±{tol:.4g} got={got:.4g}")

    def ge(self, name: str, minimum: float, got: float) -> None:
        self.checks += 1
        if got >= minimum:
            print(f"{name} OK ({got} >= {minimum})")
        else:
            self.failures += 1
            print(f"{name} MISMATCH expected>={minimum} got={got}")


def add_working_days(start: date, n: int) -> date:
    d, left = start, n
    while left > 0:
        d += timedelta(days=1)
        if d.weekday() < 5:
            left -= 1
    return d


def scalar(conn: Connection, sql: str, **params: Any) -> Any:
    return conn.execute(sa.text(sql), params).scalar()


def story(cfg: dict[str, Any], key: str) -> dict[str, Any]:
    for s in cfg["storylines"]:
        if s["key"] == key:
            return s
    raise KeyError(key)


# ---------------------------------------------------------------------------

def check_mri(r: Report, conn: Connection, s: dict, m: dict) -> None:
    p = s["params"]
    lines = int(scalar(conn, "SELECT count(*) FROM contract_lines "
                        "WHERE service_group = 'МРТ' AND care_type = 'kdu' "
                        "AND month LIKE '2026-%'"))
    r.ge("S1 МРТ contract lines (2026)", 1, lines)

    plan_qty = int(scalar(conn, "SELECT COALESCE(SUM(plan_qty),0) FROM contract_lines "
                          "WHERE service_group='МРТ' AND month BETWEEN '2026-03' AND '2026-06'"))
    fact_qty = int(scalar(conn, "SELECT count(*) FROM claims "
                          "WHERE service_code='S010' AND period BETWEEN '2026-03' AND '2026-06'"))
    ratio = fact_qty / plan_qty if plan_qty else 0.0
    r.near("S1 МРТ run-rate (Mar–Jun 2026)", float(p["monthly_run_rate"]), ratio, 0.12)

    r.eq("S1 burn_out_date", p["expected_burn_out_date"], m["mri_over_execution"]["burn_out_date"])
    r.near("S1 recoverable ₸", float(p["expected_recoverable_amount"]),
           float(m["mri_over_execution"]["recoverable_amount"]),
           float(p["expected_recoverable_amount"]) * 0.02)


def check_dent(r: Report, conn: Connection, s: dict, m: dict) -> None:
    p = s["params"]
    plan = int(scalar(conn, "SELECT COALESCE(SUM(plan_amount),0) FROM contract_lines "
                      "WHERE care_type='dent' AND month BETWEEN '2026-01' AND '2026-06'"))
    fact = int(scalar(conn, "SELECT COALESCE(SUM(amount),0) FROM claims "
                      "WHERE care_type='dent' AND status IN ('accepted','paid') "
                      "AND period BETWEEN '2026-01' AND '2026-06'"))
    ratio = fact / plan if plan else 0.0
    r.near("S2 dent YTD run-rate", float(p["run_rate"]), ratio, float(p["run_rate_tol"]))
    r.eq("S2 year-end gap ₸", int(p["expected_year_end_gap"]),
         int(m["dent_under_execution"]["expected_year_end_gap"]))


def check_creative(r: Report, conn: Connection, s: dict, m: dict) -> None:
    p = s["params"]
    peak = int(scalar(conn, "SELECT MAX(cnt) FROM (SELECT doctor_id, date_start, count(*) cnt "
                      "FROM claims GROUP BY doctor_id, date_start) t"))
    r.ge("S3 max visits/day", int(p["peak_day_visits"]), peak)
    burst_doc = scalar(conn, "SELECT doctor_id FROM claims GROUP BY doctor_id, date_start "
                       "ORDER BY count(*) DESC LIMIT 1")
    wknd = int(scalar(conn, "SELECT count(*) FROM claims WHERE doctor_id=:d "
                      "AND EXTRACT(DOW FROM date_start) IN (0,6)", d=burst_doc))
    r.ge("S3 weekend claims (burst doctor)", int(p["weekend_claims"]), wknd)


def check_posthumous(r: Report, conn: Connection, s: dict, m: dict) -> None:
    p = s["params"]
    deaths = int(scalar(conn, "SELECT count(*) FROM patients WHERE death_date IS NOT NULL"))
    r.eq("S4 patients with death_date", int(p["patients_with_death_date"]), deaths)
    after = int(scalar(conn, "SELECT count(*) FROM claims c JOIN patients p ON p.id=c.patient_id "
                       "WHERE p.death_date IS NOT NULL AND c.date_start > p.death_date"))
    r.eq("S4 claims after death", int(p["claims_after_death"]), after)


def check_sex_age(r: Report, conn: Connection, s: dict, m: dict) -> None:
    p = s["params"]
    male = int(scalar(conn, "SELECT count(*) FROM claims c JOIN patients p ON p.id=c.patient_id "
                      "WHERE c.service_code=:code AND c.period=:per AND p.sex='M'",
                      code=p["male_mammography_code"], per=p["registry_period"]))
    r.eq("S5 male mammography (2025-11)", int(p["male_mammography_claims"]), male)
    male_amt = int(scalar(conn, "SELECT COALESCE(SUM(c.amount),0) FROM claims c "
                          "JOIN patients p ON p.id=c.patient_id "
                          "WHERE c.service_code=:code AND c.period=:per AND p.sex='M'",
                          code=p["male_mammography_code"], per=p["registry_period"]))
    r.eq("S5 male mammography ₸", int(p["male_mammography_amount"]), male_amt)
    # planted underage screening = S031 (base pool is age >= 50) on <50 patients
    young = int(scalar(conn, "SELECT count(*) FROM claims c JOIN patients p ON p.id=c.patient_id "
                       "WHERE c.service_code=:code AND c.period=:per "
                       "AND (CAST(LEFT(c.period,4) AS int) - p.birth_year) < 50",
                       code=p["underage_screening_code"], per=p["registry_period"]))
    r.eq("S5 underage screening (2025-11)", int(p["underage_screening_claims"]), young)


def check_under_billing(r: Report, conn: Connection, s: dict, m: dict) -> None:
    p = s["params"]
    cnt = int(scalar(conn, "SELECT count(*) FROM claims WHERE status='mis_only'"))
    r.eq("S6 mis_only cases", int(p["mis_only_cases"]), cnt)
    amt = int(scalar(conn, "SELECT COALESCE(SUM(amount),0) FROM claims WHERE status='mis_only'"))
    r.eq("S6 mis_only ₸", int(p["expected_amount"]), amt)


def check_reform(r: Report, conn: Connection, s: dict, m: dict) -> None:
    p = s["params"]
    months = tuple(p["months"])
    cnt = int(scalar(conn, "SELECT count(*) FROM claims WHERE icd10 LIKE 'E11%' "
                     "AND funding_source=:src AND period = ANY(:months)",
                     src=p["billed_source"], months=list(months)))
    r.eq("S7 reform mis-billed claims", int(p["claims"]), cnt)
    amt = int(scalar(conn, "SELECT COALESCE(SUM(amount),0) FROM claims WHERE icd10 LIKE 'E11%' "
                     "AND funding_source=:src AND period = ANY(:months)",
                     src=p["billed_source"], months=list(months)))
    r.eq("S7 reform mis-billed ₸", int(p["expected_amount"]), amt)


def check_objections(r: Report, s: dict, m: dict, demo_today: str) -> None:
    ow = m["objection_window"]
    defects = s["defects"]
    r.eq("S8 defect count", int(s["params"]["defect_count"]), int(ow["defect_count"]))
    r.eq("S8 total ₸ at stake", int(s["params"]["total_amount_at_stake"]),
         int(ow["total_amount_at_stake"]))
    today = date.fromisoformat(demo_today)
    by_ref = {d["case_ref"]: d for d in ow["defects"]}
    for d in defects:
        expected = add_working_days(today, int(d["deadline_working_days"])).isoformat()
        got = by_ref[d["case_ref"]]["deadline_date"]
        r.eq(f"S8 deadline {d['case_ref']} ({d['deadline_working_days']}wd)", expected, got)


def check_forecast_risk(r: Report, conn: Connection, s5: dict) -> None:
    n_grain = int(scalar(conn, "SELECT count(*) FROM (SELECT DISTINCT care_type, "
                         "funding_source, COALESCE(service_group,'') FROM contract_lines "
                         "WHERE month LIKE '2026-%') t"))
    n_fc = int(scalar(conn, "SELECT count(*) FROM forecasts"))
    r.eq("F2 forecasts == 2026 line grains", n_grain, n_fc)
    n_risk = int(scalar(conn, "SELECT count(*) FROM risk_assessments"))
    r.eq("F2 risk_assessments == 2026 line grains", n_grain, n_risk)

    mri_over = int(scalar(conn, "SELECT count(*) FROM risk_assessments "
                          "WHERE service_group='МРТ' AND class='critical_over' "
                          "AND burn_out_date = DATE '2026-10-14'"))
    r.ge("F2 МРТ risk critical_over + burn_out", 1, mri_over)

    dent_gap = int(scalar(conn, "SELECT COALESCE(SUM(gap_amount),0) FROM risk_assessments "
                          "WHERE care_type='dent'"))
    r.eq("F2 dent risk gap ₸ (sum)", int(s5["params"]["expected_year_end_gap"]), dent_gap)
    dent_class = int(scalar(conn, "SELECT count(*) FROM risk_assessments "
                            "WHERE care_type='dent' AND class='critical_under'"))
    r.ge("F2 dent risk critical_under lines", 1, dent_class)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--storylines", type=Path, default=DEFAULT_STORYLINES)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args(argv)

    cfg = yaml.safe_load(args.storylines.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    m = manifest["storylines"]
    demo_today = cfg["demo_today"]
    r = Report()

    with get_engine().connect() as conn:
        check_mri(r, conn, story(cfg, "mri_over_execution"), m)
        check_dent(r, conn, story(cfg, "dent_under_execution"), m)
        check_creative(r, conn, story(cfg, "creative_doctor"), m)
        check_posthumous(r, conn, story(cfg, "posthumous_services"), m)
        check_sex_age(r, conn, story(cfg, "sex_age_mismatch_batch"), m)
        check_under_billing(r, conn, story(cfg, "under_billing"), m)
        check_reform(r, conn, story(cfg, "reform_mis_billing"), m)
        check_objections(r, story(cfg, "objection_window"), m, demo_today)
        check_forecast_risk(r, conn, story(cfg, "dent_under_execution"))

    status = "FAIL" if r.failures else "PASS"
    print(f"assert_storylines: {status} — {r.checks} checks, {r.failures} mismatches")
    return 1 if r.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
