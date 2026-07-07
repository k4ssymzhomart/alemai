"""Forecast service — explainable per-line projections (docs/06 §6).

Contract:
- Per line and month: working-day run-rate over the recent 3 months, seasonal
  index (classical decomposition when >=24m history, else per-care-type default
  profile), Holt-Winters additive when history permits, 50/50 ensemble.
- CI = residual bootstrap p10/p90 on backtest errors.
- Every stored forecast carries method, ``inputs_hash`` and a mandatory
  human-readable ``explanation`` (kk/ru) — the UI never shows a forecast
  without its "почему" (docs/04 FORESEE).
- Backtest: hold out last 3 months, report MAPE per care_type (target <=8%
  on synthetic data; honest number on real data).
- Edge cases: new line mid-year -> plan-proportional prior; zero-plan lines
  excluded; amendments change risk, not the demand forecast.
"""
