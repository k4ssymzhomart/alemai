"""Load ``backend/rules/*.yaml`` and mirror it into the ``rules`` table.

The YAML catalog is the source of truth (docs/06 §7); the DB ``rules`` table is
a mirror so ``findings.rule_code`` has a valid FK and the API can serve rule
metadata. ``sync_catalog`` is idempotent — it upserts every rule on each run.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import RuleSeverity
from app.models.rules import Rule

RULES_DIR = Path(__file__).resolve().parents[3] / "rules"


@dataclass(frozen=True, slots=True)
class RuleDef:
    """One parsed rule from the YAML catalog."""

    code: str
    severity: RuleSeverity
    scope: str
    origin: str
    ekd_code: str
    message_ru: str
    message_kk: str
    enabled: bool = True
    params: dict[str, Any] = field(default_factory=dict)

    @property
    def db_params(self) -> dict[str, Any]:
        """Params blob stored on the Rule row (ЕКД code folded in — no new column)."""
        return {"ekd_code": self.ekd_code, **self.params}


def load_catalog(rules_dir: Path | None = None) -> list[RuleDef]:
    """Parse every ``*.yaml`` under ``rules_dir`` into :class:`RuleDef`, sorted by code."""
    directory = rules_dir or RULES_DIR
    defs: dict[str, RuleDef] = {}
    for path in sorted(directory.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        for item in raw:
            code = str(item["code"])
            defs[code] = RuleDef(
                code=code,
                severity=RuleSeverity(item["severity"]),
                scope=str(item.get("scope", "claim")),
                origin=str(item.get("origin", "ЕКД")),
                ekd_code=str(item["ekd_code"]),
                message_ru=str(item["message_ru"]),
                message_kk=str(item["message_kk"]),
                enabled=bool(item.get("enabled", True)),
                params=dict(item.get("params") or {}),
            )
    return [defs[code] for code in sorted(defs)]


def sync_catalog(session: Session, catalog: list[RuleDef] | None = None) -> list[RuleDef]:
    """Upsert the catalog into the ``rules`` table (idempotent). Returns the catalog."""
    catalog = catalog if catalog is not None else load_catalog()
    existing = {row.code: row for row in session.execute(select(Rule)).scalars()}
    for rule in catalog:
        row = existing.get(rule.code)
        if row is None:
            session.add(
                Rule(
                    code=rule.code,
                    severity=rule.severity,
                    scope=rule.scope,
                    enabled=rule.enabled,
                    params=rule.db_params,
                    message_kk=rule.message_kk,
                    message_ru=rule.message_ru,
                    origin=rule.origin,
                )
            )
        else:
            row.severity = rule.severity
            row.scope = rule.scope
            row.enabled = rule.enabled
            row.params = rule.db_params
            row.message_kk = rule.message_kk
            row.message_ru = rule.message_ru
            row.origin = rule.origin
    session.flush()
    return catalog
