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
        if "get" in operations:
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
