"""Ingest service — adapter-based file imports (docs/05 §3, docs/06 §1-§2).

Contract:
- One adapter per source kind (contract | amendment | mis | fund_statement | rpn),
  each described by a mapping YAML so real-data column drift is a config change,
  not a code change (docs/06 §2 step 3).
- Every upload produces an ``import_files`` row with rows_ok / rows_quarantined /
  control_sum; rows failing validation land in ``quarantine_rows`` with per-row
  error lists — imports never silently drop data.
- Patient identifiers are salted-SHA-256 hashed at the boundary (docs/04 §6);
  raw identifiers are never persisted.
- Performance target: 50k rows < 60s with progress reporting (docs/04 §4).
"""
