"""EPIC G1 auth — login/session/curator-scope against the seeded DB.

Auto-skipped when the DB is unreachable or the users weren't seeded (same
contract as the other integration modules).
"""

import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.main import app

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def client() -> TestClient:
    engine = sa.create_engine(
        get_settings().database_url, connect_args={"connect_timeout": 2}
    )
    try:
        with engine.connect() as conn:
            seeded = conn.execute(
                sa.text("SELECT 1 FROM users WHERE username = 'economist'")
            ).first()
    except SQLAlchemyError as exc:
        pytest.skip(f"database unreachable: {type(exc).__name__}")
    finally:
        engine.dispose()
    if seeded is None:
        pytest.skip("users not seeded — run `python -m app.seed`")
    return TestClient(app)


def _login(client: TestClient, username: str) -> TestClient:
    resp = client.post(
        "/api/v1/auth/login", json={"username": username, "password": "qalam2026"}
    )
    assert resp.status_code == 200, resp.text
    return client


def test_login_sets_session_and_me_returns_identity(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/auth/login", json={"username": "economist", "password": "qalam2026"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["role"] == "economist" and body["name"] == "Айгерім"
    assert get_settings().session_cookie in resp.cookies

    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["username"] == "economist"


def test_wrong_password_401(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/auth/login", json={"username": "economist", "password": "nope"}
    )
    assert resp.status_code == 401


def test_me_without_session_401(client: TestClient) -> None:
    fresh = TestClient(app)
    assert fresh.get("/api/v1/auth/me").status_code == 401


def test_all_five_users_login(client: TestClient) -> None:
    for username in ("director", "economist", "statistician", "curator", "admin"):
        fresh = TestClient(app)
        resp = fresh.post(
            "/api/v1/auth/login", json={"username": username, "password": "qalam2026"}
        )
        assert resp.status_code == 200, username


def test_curator_denied_patient_level_but_allowed_aggregate(client: TestClient) -> None:
    curator = TestClient(app)
    _login(curator, "curator")
    # patient/case-level → 403
    assert curator.get("/api/v1/reconcile/bucket/1/rows").status_code == 403
    # aggregate → 200
    assert curator.get("/api/v1/reconcile/buckets").status_code == 200


def test_economist_allowed_patient_level(client: TestClient) -> None:
    econ = TestClient(app)
    _login(econ, "economist")
    assert econ.get("/api/v1/reconcile/bucket/1/rows?limit=1").status_code == 200


def test_service_token_bypasses_curator_scope(client: TestClient) -> None:
    fresh = TestClient(app)
    resp = fresh.get(
        "/api/v1/reconcile/bucket/1/rows?limit=1",
        headers={"X-Service-Token": get_settings().service_token},
    )
    assert resp.status_code == 200


def test_curator_denied_case_level_xlsx_exports(client: TestClient) -> None:
    """Adversarial review #2: XLSX exports must honour curator scope too."""
    curator = TestClient(app)
    _login(curator, "curator")
    assert curator.get("/api/v1/exports/prebilling.xlsx").status_code == 403
    assert curator.get("/api/v1/exports/reconcile-bucket/1.xlsx").status_code == 403
    # aggregate export stays open
    assert curator.get("/api/v1/exports/overview.xlsx").status_code == 200
    econ = TestClient(app)
    _login(econ, "economist")
    assert econ.get("/api/v1/exports/prebilling.xlsx").status_code == 200


def test_thresholds_put_requires_auth_and_denies_curator(client: TestClient) -> None:
    """Adversarial review #4: threshold mutation is privileged."""
    body = {"under_pct": 90, "over_pct": 105, "burnout_days": 45,
            "materiality_tenge": 100000}
    anon = TestClient(app)
    assert anon.put("/api/v1/admin/thresholds", json=body).status_code == 401
    curator = TestClient(app)
    _login(curator, "curator")
    assert curator.put("/api/v1/admin/thresholds", json=body).status_code == 403
    admin = TestClient(app)
    _login(admin, "admin")
    assert admin.put("/api/v1/admin/thresholds", json=body).status_code == 200
