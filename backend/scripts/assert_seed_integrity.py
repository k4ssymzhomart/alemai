#!/usr/bin/env python3
"""Cross-check seeded DB vs datagen manifest vs metrics API; exit 1 on mismatch.

Three layers of proof (docs/11 §3 P1 AC):

1. DB vs manifest — per-table row counts; claims count/total_amount/
   by_status/by_care_type/by_funding_source/by_year sums; plan by-year sums
   checked BOTH against the mv_line_execution plan side AND against
   contract_lines directly.
2. API vs DB — /metrics/overview numbers must equal aggregates recomputed
   here with raw SQL over claims/contract_lines (deliberately NOT via
   app.services.metrics.queries, so this is a real cross-check of C4/C5).
3. API self-consistency — sum of /metrics/lines fact_amount_ytd equals the
   overview; items sorted by plan_amount_year DESC; one sampled line's
   /monthly sums equal its lines row, cumulative columns are true running
   totals.

Usage:
    python scripts/assert_seed_integrity.py /tmp/igerim_seed/manifest.json [--api-base URL]

Default API access is in-process (fastapi TestClient importing app.main);
pass --api-base http://host:port to hit a live server instead.

Output: one line per check — '<CHECK> OK (value)' or
'<CHECK> MISMATCH expected=... got=...'.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # import 'app' when run as script

import sqlalchemy as sa  # noqa: E402
from sqlalchemy.engine import Connection  # noqa: E402

from app.db import get_engine  # noqa: E402


class Report:
    """Collects check results; prints one line per check."""

    def __init__(self) -> None:
        self.checks = 0
        self.failures = 0

    def check(self, name: str, expected: object, got: object) -> None:
        self.checks += 1
        if expected == got:
            print(f"{name} OK ({got})")
        else:
            self.failures += 1
            print(f"{name} MISMATCH expected={expected} got={got}")


class ApiClient:
    """GET JSON either in-process (TestClient) or over live HTTP (httpx)."""

    def __init__(self, api_base: str | None) -> None:
        if api_base is None:
            from fastapi.testclient import TestClient

            from app.main import app

            self._client: Any = TestClient(app)
        else:
            import httpx

            self._client = httpx.Client(base_url=api_base, timeout=30.0)

    def get_json(self, path: str, **params: Any) -> dict[str, Any]:
        response = self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()


# ---------------------------------------------------------------------------
# 1. DB vs manifest
# ---------------------------------------------------------------------------


def check_row_counts(report: Report, conn: Connection, manifest: dict[str, Any]) -> None:
    for table, expected in manifest["rows"].items():
        got = conn.execute(sa.text(f"SELECT count(*) FROM {table}")).scalar_one()
        report.check(f"ROWS {table}", int(expected), int(got))


def check_claims(report: Report, conn: Connection, manifest: dict[str, Any]) -> None:
    m = manifest["claims"]
    count, total = conn.execute(
        sa.text("SELECT count(*), COALESCE(SUM(amount), 0) FROM claims")
    ).one()
    report.check("CLAIMS count", int(m["count"]), int(count))
    report.check("CLAIMS total_amount", int(m["total_amount"]), int(total))

    db_status = {
        status: (int(cnt), int(amount))
        for status, cnt, amount in conn.execute(
            sa.text("SELECT status, count(*), SUM(amount) FROM claims GROUP BY status")
        )
    }
    report.check("CLAIMS by_status keys", sorted(m["by_status"]), sorted(db_status))
    for status, expected in m["by_status"].items():
        got_count, got_amount = db_status.get(status, (0, 0))
        report.check(f"CLAIMS by_status[{status}].count", int(expected["count"]), got_count)
        report.check(f"CLAIMS by_status[{status}].amount", int(expected["amount"]), got_amount)

    for manifest_key, column in (
        ("by_care_type_amount", "care_type"),
        ("by_funding_source_amount", "funding_source"),
    ):
        db_map = {
            key: int(amount)
            for key, amount in conn.execute(
                sa.text(f"SELECT {column}, SUM(amount) FROM claims GROUP BY {column}")
            )
        }
        report.check(f"CLAIMS {manifest_key} keys", sorted(m[manifest_key]), sorted(db_map))
        for key, expected in m[manifest_key].items():
            report.check(f"CLAIMS {manifest_key}[{key}]", int(expected), db_map.get(key, 0))

    db_year = {
        year: int(amount)
        for year, amount in conn.execute(
            sa.text("SELECT LEFT(period, 4), SUM(amount) FROM claims GROUP BY LEFT(period, 4)")
        )
    }
    report.check("CLAIMS by_year_amount keys", sorted(m["by_year_amount"]), sorted(db_year))
    for year, expected in m["by_year_amount"].items():
        report.check(f"CLAIMS by_year_amount[{year}]", int(expected), db_year.get(year, 0))


def check_plan(report: Report, conn: Connection, manifest: dict[str, Any]) -> None:
    plan = manifest["plan"]
    mv_by_year = {
        int(year): (int(amount), int(qty))
        for year, amount, qty in conn.execute(
            sa.text(
                "SELECT year, SUM(plan_amount), SUM(plan_qty) "
                "FROM mv_line_execution GROUP BY year"
            )
        )
    }
    cl_by_year = {
        int(year): (int(amount), int(qty))
        for year, amount, qty in conn.execute(
            sa.text(
                "SELECT c.year, SUM(cl.plan_amount), SUM(cl.plan_qty) "
                "FROM contract_lines cl JOIN contracts c ON c.id = cl.contract_id "
                "GROUP BY c.year"
            )
        )
    }
    for source, by_year in (("mv_line_execution", mv_by_year), ("contract_lines", cl_by_year)):
        for year, expected in plan["by_year_amount"].items():
            got = by_year.get(int(year), (0, 0))[0]
            report.check(f"PLAN {source} by_year_amount[{year}]", int(expected), got)
        for year, expected in plan["by_year_qty"].items():
            got = by_year.get(int(year), (0, 0))[1]
            report.check(f"PLAN {source} by_year_qty[{year}]", int(expected), got)


# ---------------------------------------------------------------------------
# 2.+3. API vs independent SQL, and API self-consistency
# ---------------------------------------------------------------------------

_SUM_CLAIMS_YTD = (
    "SELECT COALESCE(SUM(amount), 0) FROM claims "
    "WHERE status = ANY(:statuses) AND period BETWEEN :start AND :end"
)


def _claims_sum(conn: Connection, statuses: list[str], start: str, end: str) -> int:
    return int(
        conn.execute(
            sa.text(_SUM_CLAIMS_YTD), {"statuses": statuses, "start": start, "end": end}
        ).scalar_one()
    )


def check_api_overview(
    report: Report, conn: Connection, api: ApiClient, year: int
) -> dict[str, Any]:
    """Overview vs raw-SQL aggregates (C4 semantics recomputed independently)."""
    overview = api.get_json("/api/v1/metrics/overview", year=year)
    as_of = conn.execute(
        sa.text("SELECT MAX(period) FROM claims WHERE period BETWEEN :start AND :end"),
        {"start": f"{year}-01", "end": f"{year}-12"},
    ).scalar()
    report.check(f"API overview[{year}].as_of", as_of, overview["as_of"])
    if as_of is None:
        for field in ("plan_amount_ytd", "fact_amount_ytd", "billed_amount_ytd",
                      "rejected_amount_ytd", "rejected_amount_mtd"):
            report.check(f"API overview[{year}].{field}", 0, overview[field])
        report.check(f"API overview[{year}].execution_pct_ytd", 0.0, overview["execution_pct_ytd"])
        return overview

    start = f"{year}-01"
    plan_ytd = int(
        conn.execute(
            sa.text(
                "SELECT COALESCE(SUM(cl.plan_amount), 0) "
                "FROM contract_lines cl JOIN contracts c ON c.id = cl.contract_id "
                "WHERE c.year = :year AND cl.month BETWEEN :start AND :end"
            ),
            {"year": year, "start": start, "end": as_of},
        ).scalar_one()
    )
    fact_ytd = _claims_sum(conn, ["accepted", "paid"], start, as_of)
    billed_ytd = _claims_sum(conn, ["submitted", "accepted", "paid"], start, as_of)
    rejected_ytd = _claims_sum(conn, ["rejected"], start, as_of)
    rejected_mtd = _claims_sum(conn, ["rejected"], as_of, as_of)
    execution = round(fact_ytd / plan_ytd * 100, 2) if plan_ytd else 0.0

    report.check(f"API overview[{year}].plan_amount_ytd", plan_ytd, overview["plan_amount_ytd"])
    report.check(f"API overview[{year}].fact_amount_ytd", fact_ytd, overview["fact_amount_ytd"])
    report.check(
        f"API overview[{year}].billed_amount_ytd", billed_ytd, overview["billed_amount_ytd"]
    )
    report.check(
        f"API overview[{year}].rejected_amount_ytd", rejected_ytd, overview["rejected_amount_ytd"]
    )
    report.check(
        f"API overview[{year}].rejected_amount_mtd", rejected_mtd, overview["rejected_amount_mtd"]
    )
    report.check(
        f"API overview[{year}].execution_pct_ytd", execution, overview["execution_pct_ytd"]
    )
    return overview


def check_api_lines(
    report: Report, api: ApiClient, year: int, overview: dict[str, Any]
) -> list[dict[str, Any]]:
    lines = api.get_json("/api/v1/metrics/lines", year=year)
    items = lines["items"]
    report.check(f"API lines[{year}] total==len(items)", lines["total"], len(items))
    report.check(
        f"API lines[{year}] sum(fact_amount_ytd)==overview",
        overview["fact_amount_ytd"],
        sum(item["fact_amount_ytd"] for item in items),
    )
    plans = [item["plan_amount_year"] for item in items]
    is_sorted = all(a >= b for a, b in zip(plans, plans[1:], strict=False))
    report.check(f"API lines[{year}] sorted plan_amount_year desc", True, is_sorted)
    return items


def check_api_monthly(report: Report, api: ApiClient, year: int, item: dict[str, Any]) -> None:
    key = item["line_key"]
    monthly = api.get_json(f"/api/v1/metrics/line/{key}/monthly", year=year)
    months = monthly["months"]
    report.check(f"API monthly[{key}] month numbers", list(range(1, 13)),
                 [m["month"] for m in months])
    report.check(
        f"API monthly[{key}] sum(plan_amount)==lines.plan_amount_year",
        item["plan_amount_year"],
        sum(m["plan_amount"] for m in months),
    )
    # as_of = MAX(period) of the year's claims, so no fact exists past it and
    # the 12-month fact sums must equal the lines row's YTD numbers.
    for monthly_field, lines_field in (
        ("fact_amount", "fact_amount_ytd"),
        ("fact_qty", "fact_qty_ytd"),
        ("billed_amount", "billed_amount_ytd"),
        ("rejected_amount", "rejected_amount_ytd"),
    ):
        report.check(
            f"API monthly[{key}] sum({monthly_field})==lines.{lines_field}",
            item[lines_field],
            sum(m[monthly_field] for m in months),
        )
    running_plan = 0
    running_fact = 0
    cumulative_ok = True
    for m in months:
        running_plan += m["plan_amount"]
        running_fact += m["fact_amount"]
        if (m["cumulative_plan_amount"], m["cumulative_fact_amount"]) != (
            running_plan,
            running_fact,
        ):
            cumulative_ok = False
    report.check(f"API monthly[{key}] cumulative columns are running totals", True, cumulative_ok)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("manifest", type=Path, help="path to datagen manifest.json")
    parser.add_argument("--api-base", default=None,
                        help="live API base URL (default: in-process TestClient)")
    args = parser.parse_args(argv)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    report = Report()
    api = ApiClient(args.api_base)

    with get_engine().connect() as conn:
        check_row_counts(report, conn, manifest)
        check_claims(report, conn, manifest)
        check_plan(report, conn, manifest)

        years = sorted(int(year) for year in manifest["claims"]["by_year_amount"])
        latest_items: list[dict[str, Any]] = []
        for year in years:
            overview = check_api_overview(report, conn, api, year)
            latest_items = check_api_lines(report, api, year, overview)
        if years and latest_items:
            check_api_monthly(report, api, years[-1], latest_items[0])

    status = "FAIL" if report.failures else "PASS"
    print(f"assert_seed_integrity: {status} — {report.checks} checks, "
          f"{report.failures} mismatches")
    return 1 if report.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
