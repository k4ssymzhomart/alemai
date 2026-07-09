"""EPIC F end-to-end: registry import round-trip against the seeded DB.

The invariant that makes the live demo upload safe: uploading the sample
registry (built from the seeded claims) matches every row, inserts nothing,
and reproduces the golden beat-4 verdict; a re-upload changes nothing.
Auto-skipped when the database is unreachable or not seeded (same contract as
test_metrics_integration).
"""

import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.main import app

pytestmark = pytest.mark.integration

GOLDEN_VERDICT = {"block_positions": 46, "block_amount": 168600, "sanction_risk": 6665700}


def _claim_counts() -> tuple[int, int]:
    engine = sa.create_engine(get_settings().database_url)
    try:
        with engine.connect() as conn:
            total, amount = conn.execute(
                sa.text("SELECT count(*), coalesce(sum(amount), 0) FROM claims")
            ).one()
        return int(total), int(amount)
    finally:
        engine.dispose()


@pytest.fixture(scope="module")
def client() -> TestClient:
    engine = sa.create_engine(
        get_settings().database_url, connect_args={"connect_timeout": 2}
    )
    try:
        with engine.connect() as conn:
            seeded = conn.execute(sa.text("SELECT 1 FROM claims LIMIT 1")).first()
    except SQLAlchemyError as exc:
        pytest.skip(f"database unreachable or not migrated: {type(exc).__name__}")
    finally:
        engine.dispose()
    if seeded is None:
        pytest.skip("claims is empty — run `python -m app.seed` first")
    return TestClient(app)


def _upload(client: TestClient, blob: bytes) -> dict:
    response = client.post(
        "/api/v1/imports/mis-registry",
        files={"file": ("registry_2025-11.xlsx", blob,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_registry_round_trip_is_idempotent(client: TestClient) -> None:
    sample = client.get("/api/v1/imports/samples/registry_2025-11.xlsx")
    assert sample.status_code == 200
    blob = sample.content
    before = _claim_counts()

    first = _upload(client, blob)
    assert first["rows_ok"] == first["rows_total"] > 0
    assert first["quarantined"] == 0
    assert first["new"] == 0 and first["updated"] == 0
    assert first["matched"] == first["rows_ok"]
    assert first["period_detected"] == "2025-11"
    for key, want in GOLDEN_VERDICT.items():
        assert first["rule_totals"][key] == want

    second = _upload(client, blob)
    assert second["matched"] == first["matched"]
    assert second["new"] == 0 and second["updated"] == 0
    assert second["claims_in_period"] == first["claims_in_period"]
    assert _claim_counts() == before  # the DB is byte-for-byte unmoved


def test_broken_registry_rows_quarantined(client: TestClient) -> None:
    sample = client.get("/api/v1/imports/samples/registry_broken.xlsx")
    assert sample.status_code == 200
    before = _claim_counts()

    result = _upload(client, sample.content)
    assert result["rows_total"] == 12
    assert result["quarantined"] == 3
    assert result["new"] == 0
    reasons = "; ".join(e for row in result["quarantine"] for e in row["errors"])
    assert "ИИН" in reasons and "тарификатор" in reasons and "сумма" in reasons

    quarantine = client.get(f"/api/v1/imports/{result['file_id']}/quarantine")
    assert quarantine.status_code == 200
    assert len(quarantine.json()["rows"]) == 3
    xlsx = client.get(f"/api/v1/exports/quarantine/{result['file_id']}.xlsx")
    assert xlsx.status_code == 200 and len(xlsx.content) > 1000
    assert _claim_counts() == before


def test_annex_preview_writes_nothing(client: TestClient) -> None:
    sample = client.get("/api/v1/imports/samples/annex_2026.xlsx")
    assert sample.status_code == 200
    before = _claim_counts()

    response = client.post(
        "/api/v1/imports/contract-annex?preview=1",
        files={"file": ("annex_2026.xlsx", sample.content,
                        "application/octet-stream")},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["preview_only"] is True
    assert body["changed"] == 2
    deltas = {line["delta"] for line in body["lines"] if line["status"] == "changed"}
    assert deltas == {5_700_000, -8_700_000}
    assert _claim_counts() == before
