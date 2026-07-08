"""End-to-end metrics API tests against a live, seeded PostgreSQL.

Marked ``integration`` and auto-skipped when the database is unreachable or
not seeded, so a DB-less ``pytest`` run stays green (smoke suite untouched).
In CI the backend job seeds a sample dataset first, so these run for real.
"""

import uuid

import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.main import app
from app.services.metrics.queries import execution_pct, parse_line_key

pytestmark = pytest.mark.integration

OVERVIEW_KEYS = {
    "year", "as_of", "plan_amount_year", "plan_amount_ytd", "fact_amount_ytd",
    "billed_amount_ytd", "rejected_amount_ytd", "rejected_amount_mtd",
    "execution_pct_ytd", "forecast_amount_year", "forecast_gap", "risk_count",
    "lines_total",
}


@pytest.fixture(scope="module")
def client() -> TestClient:
    """TestClient bound to a reachable, seeded DB — otherwise skip the module."""
    engine = sa.create_engine(
        get_settings().database_url, connect_args={"connect_timeout": 2}
    )
    try:
        with engine.connect() as conn:
            seeded = conn.execute(sa.text("SELECT 1 FROM mv_line_execution LIMIT 1")).first()
    except SQLAlchemyError as exc:
        pytest.skip(f"database unreachable or not migrated: {type(exc).__name__}")
    finally:
        engine.dispose()
    if seeded is None:
        pytest.skip("mv_line_execution is empty — run `python -m app.seed` first")
    return TestClient(app)


def test_overview_shape_and_consistency(client: TestClient) -> None:
    response = client.get("/api/v1/metrics/overview")
    assert response.status_code == 200
    body = response.json()
    assert set(body) == OVERVIEW_KEYS
    # Default year = latest with claims, so as_of must resolve (C4).
    assert body["as_of"] is not None
    assert body["as_of"].startswith(f"{body['year']}-")
    assert 0 <= body["plan_amount_ytd"] <= body["plan_amount_year"]
    assert 0 <= body["fact_amount_ytd"] <= body["billed_amount_ytd"]
    assert body["rejected_amount_mtd"] <= body["rejected_amount_ytd"]
    assert body["execution_pct_ytd"] == execution_pct(
        body["fact_amount_ytd"], body["plan_amount_ytd"]
    )
    assert body["lines_total"] > 0
    # F2 read-side: forecast/risk are populated for a year Epic B seeded
    # (default year = latest with claims). Consistency, not a hard-coded number.
    if body["forecast_amount_year"] is not None:
        assert body["forecast_gap"] == body["plan_amount_year"] - body["forecast_amount_year"]
        assert isinstance(body["risk_count"], int) and body["risk_count"] >= 0


def test_overview_year_without_data_returns_zeros(client: TestClient) -> None:
    """Documented choice: no data for a year -> 200 with zeros, as_of null."""
    response = client.get("/api/v1/metrics/overview", params={"year": 1999})
    assert response.status_code == 200
    body = response.json()
    assert body["year"] == 1999
    assert body["as_of"] is None
    for field in ("plan_amount_year", "plan_amount_ytd", "fact_amount_ytd",
                  "billed_amount_ytd", "rejected_amount_ytd", "rejected_amount_mtd",
                  "lines_total"):
        assert body[field] == 0, field
    assert body["execution_pct_ytd"] == 0.0


def test_lines_sorted_and_sum_matches_overview(client: TestClient) -> None:
    overview = client.get("/api/v1/metrics/overview").json()
    year = overview["year"]
    response = client.get("/api/v1/metrics/lines", params={"year": year})
    assert response.status_code == 200
    body = response.json()
    assert body["year"] == year
    assert body["as_of"] == overview["as_of"]
    items = body["items"]
    assert body["total"] == len(items) > 0
    plans = [item["plan_amount_year"] for item in items]
    assert plans == sorted(plans, reverse=True)
    assert sum(item["fact_amount_ytd"] for item in items) == overview["fact_amount_ytd"]
    assert sum(item["plan_amount_year"] for item in items) == overview["plan_amount_year"]
    valid_risk = {"critical_under", "under_risk", "on_track", "over_risk", "critical_over"}
    for item in items:
        parsed = parse_line_key(item["line_key"])  # every key must be valid C1
        assert str(parsed.contract_id) == item["contract_id"]
        assert item["year"] == year
        # F2 read-side: risk_class from a valid enum (or null); forecast_gap consistent.
        assert item["risk_class"] is None or item["risk_class"] in valid_risk
        if item["forecast_amount_year"] is not None:
            assert item["forecast_gap"] == item["plan_amount_year"] - item["forecast_amount_year"]


def test_lines_filters_apply(client: TestClient) -> None:
    all_lines = client.get("/api/v1/metrics/lines").json()
    sample = all_lines["items"][0]
    response = client.get(
        "/api/v1/metrics/lines",
        params={
            "year": all_lines["year"],
            "funding_source": sample["funding_source"],
            "care_type": sample["care_type"],
            "contract_id": sample["contract_id"],
        },
    )
    assert response.status_code == 200
    filtered = response.json()["items"]
    assert filtered, "the sampled line must survive its own filter"
    for item in filtered:
        assert item["funding_source"] == sample["funding_source"]
        assert item["care_type"] == sample["care_type"]
        assert item["contract_id"] == sample["contract_id"]
    assert any(item["line_key"] == sample["line_key"] for item in filtered)


def test_monthly_12_months_and_cumulative(client: TestClient) -> None:
    lines = client.get("/api/v1/metrics/lines").json()
    year, item = lines["year"], lines["items"][0]
    response = client.get(
        f"/api/v1/metrics/line/{item['line_key']}/monthly", params={"year": year}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["line_key"] == item["line_key"]
    assert body["year"] == year
    months = body["months"]
    assert [m["month"] for m in months] == list(range(1, 13))
    assert [m["period"] for m in months] == [f"{year}-{m:02d}" for m in range(1, 13)]
    running_plan = running_fact = 0
    for m in months:
        running_plan += m["plan_amount"]
        running_fact += m["fact_amount"]
        assert m["cumulative_plan_amount"] == running_plan
        assert m["cumulative_fact_amount"] == running_fact
    # as_of = MAX(period) of the year's claims, so 12-month sums == YTD row.
    assert sum(m["plan_amount"] for m in months) == item["plan_amount_year"]
    assert sum(m["fact_amount"] for m in months) == item["fact_amount_ytd"]
    assert sum(m["billed_amount"] for m in months) == item["billed_amount_ytd"]


def test_monthly_unknown_line_is_404(client: TestClient) -> None:
    ghost = f"{uuid.uuid4()}:pmsp:osms:-"
    assert client.get(f"/api/v1/metrics/line/{ghost}/monthly").status_code == 404
    # Malformed keys name a line that cannot exist -> same 404.
    assert client.get("/api/v1/metrics/line/not-a-line-key/monthly").status_code == 404
