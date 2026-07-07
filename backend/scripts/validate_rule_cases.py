"""Validate backend/tests/fixtures/rule_cases.yaml (golden-test cases for the rules engine).

Contract: a YAML list; one entry per rule code R01..R25; each entry has at least one
should_fire and one should_not_fire case; every case has a non-empty desc and a
non-empty claim mapping. These fixtures become the rules-engine golden tests.

Exit 0 with "OK: ..." on success, exit 0 with "SKIP: ..." if the file does not exist
yet, exit 1 with one line per error otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

EXPECTED_CODES = {f"R{i:02d}" for i in range(1, 26)}
FIXTURE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "rule_cases.yaml"


def main() -> int:
    if not FIXTURE.exists():
        print("SKIP: rule_cases.yaml not found yet")
        return 0

    errors: list[str] = []
    try:
        data = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"ERROR: invalid YAML: {exc}")
        return 1

    if not isinstance(data, list):
        print("ERROR: top level must be a list of rule entries")
        return 1

    seen: set[str] = set()
    total_cases = 0
    for idx, entry in enumerate(data):
        where = f"entry[{idx}]"
        if not isinstance(entry, dict):
            errors.append(f"{where}: must be a mapping")
            continue
        code = str(entry.get("rule", ""))
        if not re.fullmatch(r"R\d{2}", code) or code not in EXPECTED_CODES:
            errors.append(f"{where}: rule={code!r} is not one of R01..R25")
            continue
        if code in seen:
            errors.append(f"{where}: duplicate entry for {code}")
        seen.add(code)
        for kind in ("should_fire", "should_not_fire"):
            cases = entry.get(kind)
            if not isinstance(cases, list) or not cases:
                errors.append(f"{code}: needs a non-empty '{kind}' list")
                continue
            for cidx, case in enumerate(cases):
                cwhere = f"{code}.{kind}[{cidx}]"
                if not isinstance(case, dict):
                    errors.append(f"{cwhere}: must be a mapping")
                    continue
                if not str(case.get("desc", "")).strip():
                    errors.append(f"{cwhere}: empty desc")
                claim = case.get("claim")
                if not isinstance(claim, dict) or not claim:
                    errors.append(f"{cwhere}: claim must be a non-empty mapping")
                total_cases += 1

    missing = EXPECTED_CODES - seen
    if missing:
        errors.append(f"missing rules: {', '.join(sorted(missing))}")

    if errors:
        print("\n".join(errors))
        return 1
    print(f"OK: {len(seen)} rules, {total_cases} cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
