"""Rules engine — YAML catalog evaluator (docs/05 §1, docs/06 §7).

Contract:
- Loads ``backend/rules/*.yaml`` (R01..R25); each rule compiles to a SQL/pandas
  predicate — domain experts can read and edit rules without a deploy.
- Runs on import, on demand (POST /rules/run) and pre-billing; findings are
  idempotent per (run, rule, claim) and store amount_at_risk plus evidence
  details.
- Severity semantics: block = exclude from registry, warn = review, info.
- Every finding message is bilingual (message_kk / message_ru) and cites the
  rule origin tag ([ЕКД] | [АУДИТ] | [СВЕРКА] | [2026]).
- Performance target: 50k claims < 30s (docs/04 §4); golden tests per rule
  against planted storylines (docs/05 §9).
"""

from app.services.rules_engine.catalog import RuleDef, load_catalog, sync_catalog
from app.services.rules_engine.engine import RunResult, fetch_claims, run

__all__ = ["RuleDef", "RunResult", "fetch_claims", "load_catalog", "run", "sync_catalog"]
