"""Anomaly detection — explainability first (docs/06 §8, E4).

Contract:
- Per-doctor daily volume robust z-score (median/MAD), flag > 3.5.
- Template detection: Jaccard similarity of service sets across a doctor's
  same-day patients; flag clusters >= 0.9 similarity with >= 5 patients.
- Weekend/off-hours share per dept vs peers; IsolationForest over doctor-month
  feature vectors for the top-k "требует проверки" list.
- Output language is neutral («требует проверки» with reasons), never
  accusatory; every flag carries its raw evidence rows (docs/04 GUARD ethics).
"""
