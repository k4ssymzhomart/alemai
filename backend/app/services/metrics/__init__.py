"""Metrics service — the semantic layer (docs/05 §6, docs/06 §5).

Contract:
- Owns ``metrics.yaml``: ~15 whitelisted metric definitions (execution_pct,
  plan/fact amounts, снято, недовыставлено, forecast_gap, burn_out_date,
  findings_count, paid_lag_days, defect_rate, forecast_mape ...) with allowed
  dimensions (month, care_type, source, dept, doctor).
- ``run_metric_query(metric, filters, period, group_by)`` is the ONLY way any
  consumer — dashboard or copilot — obtains numbers; the server builds SQL from
  the definitions, the LLM never writes SQL.
- Dashboard aggregates read the ``mv_line_execution`` materialized view,
  refreshed after imports and rule runs (NFR: <2s p95, docs/05 §4).
"""
