"""Reconciliation — money finders, not defects (docs/06 §7 [СВЕРКА], B3).

Contract — four buckets, each with ₸ total and claim-level drill-down:
- X1: rendered in MIS but never billed (недовыставление) — recoverable money.
- X2: billed on the portal but absent in the MIS export.
- X3: accepted but unpaid, aging > 45 days.
- X4: amount mismatch between MIS and portal statements for the same claim.
Bucket totals must exactly match planted storyline numbers on seed data
(docs/06 §10 — e.g. X1 = 4.2 mln ₸).
"""
