"""EPIC G2/G3 events — writers + feed + unread + mark-read against seeded DB."""

import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.main import app

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def seeded() -> bool:
    engine = sa.create_engine(
        get_settings().database_url, connect_args={"connect_timeout": 2}
    )
    try:
        with engine.connect() as conn:
            ok = conn.execute(
                sa.text("SELECT 1 FROM users WHERE username='economist'")
            ).first()
    except SQLAlchemyError as exc:
        pytest.skip(f"database unreachable: {type(exc).__name__}")
    finally:
        engine.dispose()
    if ok is None:
        pytest.skip("users not seeded")
    return True


def _client(username: str) -> TestClient:
    c = TestClient(app)
    assert c.post(
        "/api/v1/auth/login", json={"username": username, "password": "qalam2026"}
    ).status_code == 200
    return c


def test_rules_run_writes_event(seeded: bool) -> None:
    econ = _client("economist")
    econ.post("/api/v1/rules/run", json={"scope": "period:2025-11"})
    feed = econ.get("/api/v1/events").json()
    types = {e["type"] for e in feed["items"]}
    assert "rules_run_finished" in types
    run_event = next(e for e in feed["items"] if e["type"] == "rules_run_finished")
    assert run_event["actor"] == "Айгерім"
    assert run_event["title_ru"] and run_event["title_kk"]


def test_finding_exclude_writes_event_and_cross_user_unread(seeded: bool) -> None:
    econ = _client("economist")
    run = econ.post("/api/v1/rules/run", json={"scope": "period:2025-11"}).json()
    fid = econ.get(
        f"/api/v1/rules/runs/{run['run_id']}/findings?limit=1"
    ).json()["findings"][0]["id"]
    resp = econ.patch(f"/api/v1/findings/{fid}", json={"status": "excluded"})
    assert resp.status_code == 200

    # A different user sees the event as unread, then can clear it.
    dana = _client("statistician")
    feed = dana.get("/api/v1/events").json()
    assert any(e["type"] == "finding_excluded" for e in feed["items"])
    assert feed["unread"] > 0
    marked = dana.post("/api/v1/events/read").json()
    assert marked["unread"] == 0
    assert dana.get("/api/v1/events").json()["unread"] == 0


def test_threshold_update_writes_event(seeded: bool) -> None:
    admin = _client("admin")
    before = admin.get("/api/v1/admin/thresholds").json()
    admin.put(
        "/api/v1/admin/thresholds",
        json={**before, "under_pct": before["under_pct"] - 1},
    )
    feed = admin.get("/api/v1/events").json()
    assert any(e["type"] == "threshold_changed" for e in feed["items"])
    # restore
    admin.put("/api/v1/admin/thresholds", json=before)
