#!/usr/bin/env python3
"""Validate every backend/rules/*.yaml against the catalog contract (docs/06 §7).

Checks per file: top level is a list of rule mappings. Per rule: code matches
R\\d\\d and is unique across all files; severity in {block, warn, info}; scope,
origin, message_ru, message_kk are non-empty strings; message_ru differs from
message_kk; params, when present, is a mapping.

Exit 0 and print "OK: N rules" on success; exit 1 with one line per error.
"""

import re
import sys
from pathlib import Path

import yaml

RULES_DIR = Path(__file__).resolve().parents[1] / "rules"
CODE_RE = re.compile(r"^R\d\d$")
SEVERITIES = {"block", "warn", "info"}
REQUIRED_STR_FIELDS = ("code", "severity", "scope", "origin", "message_ru", "message_kk")


def validate_rule(rule: object, where: str, seen_codes: dict[str, str]) -> list[str]:
    errors: list[str] = []
    if not isinstance(rule, dict):
        return [f"{where}: rule must be a mapping, got {type(rule).__name__}"]

    for field in REQUIRED_STR_FIELDS:
        value = rule.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{where}: field '{field}' is required and must be a non-empty string")

    code = rule.get("code")
    if isinstance(code, str) and code.strip():
        if not CODE_RE.match(code):
            errors.append(f"{where}: code '{code}' does not match R\\d\\d")
        elif code in seen_codes:
            errors.append(
                f"{where}: duplicate code '{code}' (already defined in {seen_codes[code]})"
            )
        else:
            seen_codes[code] = where

    severity = rule.get("severity")
    if isinstance(severity, str) and severity.strip() and severity not in SEVERITIES:
        errors.append(f"{where}: severity '{severity}' not in {sorted(SEVERITIES)}")

    message_ru = rule.get("message_ru")
    message_kk = rule.get("message_kk")
    if (
        isinstance(message_ru, str)
        and isinstance(message_kk, str)
        and message_ru.strip()
        and message_ru.strip() == message_kk.strip()
    ):
        errors.append(f"{where}: message_ru and message_kk must differ")

    params = rule.get("params")
    if params is not None and not isinstance(params, dict):
        errors.append(f"{where}: params must be a mapping when present")

    return errors


def main() -> int:
    files = sorted(RULES_DIR.glob("*.yaml"))
    if not files:
        print(f"ERROR: no rule files found in {RULES_DIR}")
        return 1

    errors: list[str] = []
    seen_codes: dict[str, str] = {}
    total = 0

    for path in files:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{path.name}: invalid YAML: {exc}")
            continue
        if not isinstance(data, list):
            errors.append(f"{path.name}: top level must be a list of rule objects")
            continue
        for index, rule in enumerate(data):
            total += 1
            errors.extend(validate_rule(rule, f"{path.name}[{index}]", seen_codes))

    if errors:
        for line in errors:
            print(line)
        return 1

    print(f"OK: {total} rules")
    return 0


if __name__ == "__main__":
    sys.exit(main())
