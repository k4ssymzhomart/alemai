"""API smoke tests (docs/05 §9): /healthz and every GET stub route return 200.

Must pass with no database available — the app is import-safe and lazy.
"""

import re
import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.smoke

client = TestClient(app)

# GET routes that read the live database (P1 real metrics, EPIC F exchange) —
# covered by tests/test_metrics_integration.py / test_imports_integration.py
# instead; smoke stays DB-free by design. /auth/me legitimately 401s without a
# session (covered by test_auth_integration.py).
DB_BACKED_PATHS = {
    "/api/v1/auth/me",
    "/api/v1/events",
    "/api/v1/admin/thresholds",
    "/api/v1/metrics/overview",
    "/api/v1/metrics/lines",
    "/api/v1/metrics/line/{line_key}/monthly",
    "/api/v1/imports/{file_id}/quarantine",
    "/api/v1/imports/samples/{filename}",
    "/api/v1/exports/prebilling.xlsx",
    "/api/v1/exports/overview.xlsx",
    "/api/v1/exports/reconcile-bucket/{bucket_no}.xlsx",
    "/api/v1/exports/quarantine/{file_id}.xlsx",
}


def _sample_value(param_name: str) -> str:
    if param_name.endswith("_id"):
        return str(uuid.uuid4())
    if param_name.endswith("_no"):
        return "1"
    return "demo-key"


def _all_get_paths() -> list[str]:
    """Every GET path from the OpenAPI schema, path params filled with samples."""
    schema = client.get("/openapi.json").json()
    paths: set[str] = set()
    for path, operations in schema["paths"].items():
        if "get" in operations and path not in DB_BACKED_PATHS:
            paths.add(re.sub(r"\{([^}]+)\}", lambda m: _sample_value(m.group(1)), path))
    return sorted(paths)


def test_healthz() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_schema_builds() -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200


@pytest.mark.parametrize("path", _all_get_paths())
def test_every_get_route_returns_200(path: str) -> None:
    response = client.get(path)
    assert response.status_code == 200, f"GET {path} -> {response.status_code}: {response.text}"
