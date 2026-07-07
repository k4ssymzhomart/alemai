#!/usr/bin/env python3
"""Validate shared/glossary.csv — the single terminology source (docs/04 §5).

Checks: header is exactly ``key,kk,ru,en``; every cell non-empty; keys unique
and snake_case ascii. The file lives at ../shared/glossary.csv relative to
backend/, resolved robustly from the repo root.

Exit 0 with "OK: N glossary rows" on success; exit 1 with one line per error.
If the file does not exist yet, print "SKIP: glossary.csv not found yet" and
exit 0 — another workstream owns creating it.
"""

import csv
import re
import sys
from pathlib import Path

EXPECTED_COLUMNS = ["key", "kk", "ru", "en"]
KEY_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")


def glossary_path() -> Path:
    repo_root = Path(__file__).resolve().parents[2]  # scripts/ -> backend/ -> repo root
    return repo_root / "shared" / "glossary.csv"


def main() -> int:
    path = glossary_path()
    if not path.is_file():
        print("SKIP: glossary.csv not found yet")
        return 0

    errors: list[str] = []
    rows = 0
    seen_keys: dict[str, int] = {}

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            print(f"{path}: file is empty")
            return 1

        if [cell.strip() for cell in header] != EXPECTED_COLUMNS:
            print(
                f"{path}: header must be exactly '{','.join(EXPECTED_COLUMNS)}', "
                f"got '{','.join(header)}'"
            )
            return 1

        for line_no, row in enumerate(reader, start=2):
            rows += 1
            if len(row) != len(EXPECTED_COLUMNS):
                errors.append(
                    f"line {line_no}: expected {len(EXPECTED_COLUMNS)} cells, got {len(row)}"
                )
                continue
            for column, cell in zip(EXPECTED_COLUMNS, row, strict=True):
                if not cell.strip():
                    errors.append(f"line {line_no}: empty cell in column '{column}'")
            key = row[0].strip()
            if key:
                if not KEY_RE.match(key):
                    errors.append(f"line {line_no}: key '{key}' is not snake_case ascii")
                if key in seen_keys:
                    errors.append(
                        f"line {line_no}: duplicate key '{key}' "
                        f"(first seen on line {seen_keys[key]})"
                    )
                else:
                    seen_keys[key] = line_no

    if errors:
        for line in errors:
            print(line)
        return 1

    print(f"OK: {rows} glossary rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
