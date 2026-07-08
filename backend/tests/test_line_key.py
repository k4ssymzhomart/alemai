"""Pure unit tests for the C1 line_key helpers — no database, no app import."""

import uuid

import pytest

from app.services.metrics.queries import (
    LineKeyError,
    ParsedLineKey,
    format_line_key,
    parse_line_key,
)

CONTRACT_ID = uuid.UUID("12345678-1234-5678-1234-567812345678")


def test_format_with_service_group() -> None:
    key = format_line_key(CONTRACT_ID, "kdu", "osms", "МРТ")
    assert key == f"{CONTRACT_ID}:kdu:osms:МРТ"


@pytest.mark.parametrize("service_group", ["", None, "-"])
def test_format_empty_service_group_becomes_dash(service_group: str | None) -> None:
    key = format_line_key(CONTRACT_ID, "pmsp", "gobmp", service_group)
    assert key == f"{CONTRACT_ID}:pmsp:gobmp:-"


def test_parse_round_trip() -> None:
    key = format_line_key(CONTRACT_ID, "dent", "osms", "stomatology")
    parsed = parse_line_key(key)
    assert parsed == ParsedLineKey(CONTRACT_ID, "dent", "osms", "stomatology")
    assert str(parsed) == key


def test_parse_dash_normalizes_to_empty_service_group() -> None:
    parsed = parse_line_key(f"{CONTRACT_ID}:pmsp:gobmp:-")
    assert parsed.service_group == ""  # matches the MV's COALESCEd '' (C2)
    # ...and formats back to the canonical '-' form.
    assert str(parsed) == f"{CONTRACT_ID}:pmsp:gobmp:-"


def test_parse_keeps_colons_inside_service_group() -> None:
    parsed = parse_line_key(f"{CONTRACT_ID}:kdu:osms:МРТ:головного мозга")
    assert parsed.service_group == "МРТ:головного мозга"


def test_parse_accepts_string_uuid_case_insensitively() -> None:
    parsed = parse_line_key(f"{str(CONTRACT_ID).upper()}:kdu:osms:-")
    assert parsed.contract_id == CONTRACT_ID


@pytest.mark.parametrize(
    "bad_key",
    [
        "",
        "no-colons-at-all",
        "only:two:parts",  # 3 segments, not 4
        f"{CONTRACT_ID}::osms:-",  # empty care_type
        f"{CONTRACT_ID}:kdu::-",  # empty funding_source
        "not-a-uuid:kdu:osms:-",
        ":kdu:osms:-",  # empty contract_id
    ],
)
def test_parse_rejects_malformed_keys(bad_key: str) -> None:
    with pytest.raises(LineKeyError):
        parse_line_key(bad_key)
