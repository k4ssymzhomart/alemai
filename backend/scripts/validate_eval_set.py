"""Validate backend/eval/copilot_eval.yaml (the 24-question copilot eval set, docs/07 §6).

Contract: a YAML list of exactly 24 entries with ids 1..24; each entry has lang
(kk|ru|en|mixed), category (data|regulation|guardrail), a non-empty question, and an
expect mapping with a known type. Data/regulation questions must carry a checkable
expectation (value / contains / cites); guardrail types may stand alone.

Exit 0 with "OK: ..." on success, exit 0 with "SKIP: ..." if the file does not exist
yet, exit 1 with one line per error otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

EVAL_FILE = Path(__file__).resolve().parents[1] / "eval" / "copilot_eval.yaml"
LANGS = {"kk", "ru", "en", "mixed"}
CATEGORIES = {"data", "regulation", "guardrail"}
EXPECT_TYPES = {
    "number", "list", "citation", "refusal", "out_of_scope", "no_data", "consistent_with",
}
SELF_SUFFICIENT = {"refusal", "out_of_scope", "no_data"}


def main() -> int:
    if not EVAL_FILE.exists():
        print("SKIP: copilot_eval.yaml not found yet")
        return 0

    errors: list[str] = []
    try:
        data = yaml.safe_load(EVAL_FILE.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"ERROR: invalid YAML: {exc}")
        return 1

    if not isinstance(data, list):
        print("ERROR: top level must be a list of eval entries")
        return 1
    if len(data) != 24:
        errors.append(f"expected exactly 24 entries, found {len(data)}")

    seen_ids: set[int] = set()
    for idx, entry in enumerate(data if isinstance(data, list) else []):
        where = f"entry[{idx}]"
        if not isinstance(entry, dict):
            errors.append(f"{where}: must be a mapping")
            continue
        eid = entry.get("id")
        if not isinstance(eid, int) or not 1 <= eid <= 24:
            errors.append(f"{where}: id must be an int in 1..24, got {eid!r}")
        elif eid in seen_ids:
            errors.append(f"{where}: duplicate id {eid}")
        else:
            seen_ids.add(eid)
            where = f"id={eid}"
        if entry.get("lang") not in LANGS:
            errors.append(f"{where}: lang must be one of {sorted(LANGS)}")
        if entry.get("category") not in CATEGORIES:
            errors.append(f"{where}: category must be one of {sorted(CATEGORIES)}")
        if not str(entry.get("question", "")).strip():
            errors.append(f"{where}: empty question")
        expect = entry.get("expect")
        if not isinstance(expect, dict):
            errors.append(f"{where}: expect must be a mapping")
            continue
        etype = expect.get("type")
        if etype not in EXPECT_TYPES:
            errors.append(f"{where}: expect.type must be one of {sorted(EXPECT_TYPES)}")
            continue
        if etype not in SELF_SUFFICIENT:
            checkable = {"value", "contains", "cites", "of_question"}
            if not checkable & set(expect):
                errors.append(
                    f"{where}: expect.type={etype} needs one of {sorted(checkable)}"
                )

    if isinstance(data, list) and len(seen_ids) == len(data):
        missing = set(range(1, 25)) - seen_ids
        if missing:
            errors.append(f"missing ids: {sorted(missing)}")

    if errors:
        print("\n".join(errors))
        return 1
    print("OK: 24 eval entries valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
