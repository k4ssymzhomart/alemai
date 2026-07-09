"""EPIC G4 ops dashboard — live counters against the seeded DB."""

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
            ok = conn.execute(sa.text("SELECT 1 FROM claims LIMIT 1")).first()
    except SQLAlchemyError as exc:
        pytest.skip(f"database unreachable: {type(exc).__name__}")
    finally:
        engine.dispose()
    if ok is None:
        pytest.skip("claims not seeded")
    return TestClient(app)


def test_dashboard_shape_and_reference_versions(client: TestClient) -> None:
    d = client.get("/api/v1/ops/dashboard", headers=_SVC).json()
    assert len(d["ref_versions"]) == 5
    assert d["last_demo_reset"]  # stamped by seed
    assert d["app_version"].startswith("QALAM")


def test_findings_dedupe_stable_across_reruns(client: TestClient) -> None:
    # Run the check twice — the deduped defect count must not double.
    for _ in range(2):
        client.post("/api/v1/rules/run", json={"scope": "period:2025-11"}, headers=_SVC)
    d = client.get("/api/v1/ops/dashboard", headers=_SVC).json()
    assert d["findings_total"] == 395
    by_sev = {c["key"]: c["count"] for c in d["findings_by_severity"]}
    assert by_sev["block"] == 46
    assert d["registries_checked"] >= 2
    assert d["positions_scanned"] == 20955  # latest run coverage, not a sum


def test_exclude_increments_sanctions_prevented(client: TestClient) -> None:
    run = client.post(
        "/api/v1/rules/run", json={"scope": "period:2025-11"}, headers=_SVC
    ).json()
    before = client.get("/api/v1/ops/dashboard", headers=_SVC).json()[
        "sanctions_prevented_tenge"
    ]
    fid = client.get(
        f"/api/v1/rules/runs/{run['run_id']}/findings?limit=1", headers=_SVC
    ).json()["findings"][0]["id"]
    client.patch(f"/api/v1/findings/{fid}", json={"status": "excluded"}, headers=_SVC)
    after = client.get("/api/v1/ops/dashboard", headers=_SVC).json()[
        "sanctions_prevented_tenge"
    ]
    assert after >= before
