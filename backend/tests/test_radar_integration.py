"""EPIC G5 normative radar — seeded statuses, confirm, finding source links.

The live /radar/check hits external mirrors, so it is exercised manually, not in
CI (kept fast + offline-safe here).
"""

import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.main import app

pytestmark = pytest.mark.integration

_SVC = {"X-Service-Token": get_settings().service_token}


@pytest.fixture(scope="module")
def client() -> TestClient:
    engine = sa.create_engine(
        get_settings().database_url, connect_args={"connect_timeout": 2}
    )
    try:
        with engine.connect() as conn:
            ok = conn.execute(sa.text("SELECT 1 FROM radar_checks LIMIT 1")).first()
    except SQLAlchemyError as exc:
        pytest.skip(f"database unreachable: {type(exc).__name__}")
    finally:
        engine.dispose()
    if ok is None:
        pytest.skip("radar_checks not seeded — run `python -m app.seed`")
    return TestClient(app)


def test_radar_seeded_states(client: TestClient) -> None:
    rows = {r["source_id"]: r for r in client.get("/api/v1/radar").json()["rows"]}
    assert len(rows) == 8  # + ФСМС provider registry (H0.4)
    assert rows["monitoring"]["status"] == "ok"
    assert rows["tarif"]["status"] == "stale"  # deliberate mock (our < official)
    assert rows["tarif"]["detected_version"] == "31.12.2025"
    assert rows["mrp_kpn"]["status"] == "manual"
    # МРП-2026 thresholds surface as real ₸ (200/800 МРП, H0.2)
    assert "865 000" in rows["mrp_kpn"]["our_version"]
    assert "3 460 000" in rows["mrp_kpn"]["our_version"]
    assert rows["providers_fsms"]["status"] == "manual"
    # every fetchable source exposes an official link
    assert all(r["official_url"].startswith("https://") for r in rows.values())


def test_confirm_marks_updated(client: TestClient) -> None:
    resp = client.post("/api/v1/radar/tarif/confirm", headers=_SVC)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["our_version"] == "31.12.2025"  # accepted the detected edition


def test_finding_carries_source_link(client: TestClient) -> None:
    run = client.post(
        "/api/v1/rules/run", json={"scope": "period:2025-11"}, headers=_SVC
    ).json()
    f = client.get(
        f"/api/v1/rules/runs/{run['run_id']}/findings?limit=1", headers=_SVC
    ).json()["findings"][0]
    assert f["details"]["source_url"] == "https://adilet.zan.kz/rus/docs/V2000021904"
    assert "Правилам мониторинга" in f["details"]["source_label"]
