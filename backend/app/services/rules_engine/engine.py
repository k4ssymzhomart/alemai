"""Rules engine — evaluate the catalog over claims and persist findings.

One :class:`~app.models.rules.RuleRun` per invocation; one
:class:`~app.models.rules.Finding` per (rule, claim) hit, idempotent within the
run. ``amount_at_risk`` is the claim's предъявлено (billed) amount — the money
that would be rejected/снято at face value — except «жёлтые» codes (2.0/7.0)
which fix 0 ₸. The ЕКД code, edition (by claim date) and the penalty-adjusted
снятие (300 % for 5.1 etc.) ride in ``details`` (see :mod:`.ekd`).

The «verdict» a pre-billing registry check renders — «N позиций / ₸ под риском»
— is the block-severity slice (:attr:`RunResult.block_positions` /
``block_amount``): the defects that would keep a claim out of the счёт-реестр.
"""

from __future__ import annotations

import datetime
import uuid
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.models.claim import Claim
from app.models.enums import RuleSeverity
from app.models.people import Patient
from app.models.rules import Finding, RuleRun
from app.services.rules_engine import ekd
from app.services.rules_engine.catalog import RuleDef, load_catalog, sync_catalog
from app.services.rules_engine.rules import EVALUATORS, ClaimRow

# mis_only claims are rendered-but-not-billed — reconcile's domain, not the
# rules engine (they never entered the счёт-реестр, so they cannot be defects).
_BILLED_STATUSES = ("submitted", "accepted", "paid", "rejected")


@dataclass(slots=True)
class RuleAgg:
    count: int = 0
    amount_at_risk: int = 0
    severity: str = "warn"
    ekd_code: str = ""


@dataclass(slots=True)
class RunResult:
    run_id: uuid.UUID
    scope: str
    duration_ms: int
    claims_scanned: int
    total_findings: int
    total_amount_at_risk: int
    block_positions: int
    block_amount: int
    by_rule: dict[str, RuleAgg] = field(default_factory=dict)

    def totals_json(self) -> dict[str, Any]:
        return {
            "scope": self.scope,
            "claims_scanned": self.claims_scanned,
            "total_findings": self.total_findings,
            "total_amount_at_risk": self.total_amount_at_risk,
            "block_positions": self.block_positions,
            "block_amount": self.block_amount,
            "duration_ms": self.duration_ms,
            "by_rule": {
                code: {
                    "count": agg.count,
                    "amount_at_risk": agg.amount_at_risk,
                    "severity": agg.severity,
                    "ekd_code": agg.ekd_code,
                }
                for code, agg in sorted(self.by_rule.items())
            },
        }


def _scope_filter(scope: str) -> sa.ColumnElement[bool] | None:
    """Translate a scope string into a WHERE predicate (None == whole DB)."""
    if scope in ("", "all"):
        return None
    kind, _, value = scope.partition(":")
    if kind == "period":
        return Claim.period == value
    if kind == "year":
        return Claim.period.like(f"{value}-%")
    if kind == "import":
        return Claim.source_file_id == uuid.UUID(value)
    return None


def fetch_claims(session: Session, scope: str = "all", limit: int | None = None) -> list[ClaimRow]:
    """Load billed claims (joined to patient attrs) for a scope into ClaimRows."""
    stmt = (
        sa.select(
            Claim.id, Claim.patient_id, Claim.doctor_id, Claim.care_type,
            Claim.funding_source, Claim.service_code, Claim.icd10, Claim.date_start,
            Claim.date_end, Claim.qty, Claim.amount, Claim.referral_id, Claim.status,
            Claim.period, Patient.sex, Patient.birth_year, Patient.death_date,
            Patient.insured,
        )
        .join(Patient, Patient.id == Claim.patient_id)
        .where(Claim.status.in_(_BILLED_STATUSES))
        .order_by(Claim.id)
    )
    predicate = _scope_filter(scope)
    if predicate is not None:
        stmt = stmt.where(predicate)
    if limit is not None:
        stmt = stmt.limit(limit)
    return [
        ClaimRow(
            id=row.id,
            patient_id=row.patient_id,
            doctor_id=row.doctor_id,
            care_type=str(row.care_type),
            funding_source=str(row.funding_source),
            service_code=row.service_code,
            icd10=row.icd10,
            date_start=row.date_start,
            date_end=row.date_end,
            qty=int(row.qty),
            amount=int(row.amount),
            referral_id=row.referral_id,
            status=str(row.status),
            period=row.period,
            sex=str(row.sex),
            birth_year=int(row.birth_year),
            death_date=row.death_date,
            insured=bool(row.insured),
        )
        for row in session.execute(stmt)
    ]


def run(
    session: Session,
    scope: str = "all",
    *,
    limit: int | None = None,
    catalog: list[RuleDef] | None = None,
) -> RunResult:
    """Sync the catalog, evaluate every enabled rule over the scope, persist findings."""
    catalog = sync_catalog(session, catalog if catalog is not None else load_catalog())
    rows = fetch_claims(session, scope, limit)

    started = perf_counter()
    run_row = RuleRun(scope=scope, started_at=datetime.datetime.now(tz=datetime.UTC))
    session.add(run_row)
    session.flush()  # assign run_row.id

    findings: list[Finding] = []
    by_rule: dict[str, RuleAgg] = {}
    seen: set[tuple[str, uuid.UUID]] = set()

    for rule in catalog:
        evaluator = EVALUATORS.get(rule.code)
        if not rule.enabled or evaluator is None:
            continue
        agg = by_rule.setdefault(
            rule.code, RuleAgg(severity=rule.severity.value, ekd_code=rule.ekd_code)
        )
        for hit in evaluator(rows, rule.params):
            claim = hit.claim
            key = (rule.code, claim.id)
            if key in seen:
                continue
            seen.add(key)
            billed = int(claim.amount)
            desc = ekd.descriptor(rule.ekd_code, claim.care_type, billed, claim.date_start)
            is_yellow = rule.severity == RuleSeverity.yellow or bool(desc["yellow"])
            amount_at_risk = 0 if is_yellow else billed
            details: dict[str, Any] = {
                **desc,
                "rule_code": rule.code,
                "severity": rule.severity.value,
                "origin": rule.origin,
                "message_ru": rule.message_ru,
                "message_kk": rule.message_kk,
                "care_type": claim.care_type,
                "funding_source": claim.funding_source,
                "service_code": claim.service_code,
                "period": claim.period,
                "patient_id": claim.patient_id,
                "amount_billed": billed,
                "evidence": hit.evidence,
            }
            findings.append(
                Finding(
                    run_id=run_row.id,
                    rule_code=rule.code,
                    claim_id=claim.id,
                    amount_at_risk=amount_at_risk,
                    details=details,
                )
            )
            agg.count += 1
            agg.amount_at_risk += amount_at_risk

    session.add_all(findings)

    block_positions = sum(
        agg.count for agg in by_rule.values() if agg.severity == RuleSeverity.block.value
    )
    block_amount = sum(
        agg.amount_at_risk for agg in by_rule.values() if agg.severity == RuleSeverity.block.value
    )
    result = RunResult(
        run_id=run_row.id,
        scope=scope,
        duration_ms=int((perf_counter() - started) * 1000),
        claims_scanned=len(rows),
        total_findings=len(findings),
        total_amount_at_risk=sum(f.amount_at_risk for f in findings),
        block_positions=block_positions,
        block_amount=block_amount,
        by_rule={code: agg for code, agg in by_rule.items() if agg.count > 0},
    )
    run_row.duration_ms = result.duration_ms
    run_row.totals = result.totals_json()
    session.flush()
    return result
