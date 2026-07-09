"""Rules engine endpoints (docs/05 §5). Real run + findings; PATCH /findings/{id}."""

import uuid
from typing import Annotated

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import DenyCurator, OptionalPrincipal
from app.db import get_db
from app.models.enums import FindingStatus
from app.models.rules import Finding, Rule
from app.schemas.rules import (
    FindingGroupOut,
    FindingOut,
    FindingPatch,
    RuleRunIn,
    RuleRunStarted,
    RunFindingsOut,
)
from app.services import events as events_svc
from app.services.rules_engine import engine

router = APIRouter(tags=["rules"])

DbDep = Annotated[Session, Depends(get_db)]
GroupByQuery = Annotated[str | None, Query(description="e.g. 'rule'")]
LimitQuery = Annotated[int, Query(ge=1, le=5000, description="max findings returned")]


@router.post("/rules/run", response_model=RuleRunStarted, status_code=202)
def run_rules(body: RuleRunIn, db: DbDep, principal: OptionalPrincipal) -> RuleRunStarted:
    """Run the ЕКД catalog over the scope, persist findings, return the summary.

    Synchronous (fast at demo scale): findings are committed before the response
    so a follow-up GET .../findings returns them. Scope: 'all' | 'period:YYYY-MM'
    | 'year:YYYY' | 'import:<uuid>'.
    """
    result = engine.run(db, scope=body.scope)
    totals = result.totals_json()
    events_svc.rules_run_finished(db, principal, scope=result.scope, totals=totals)
    db.commit()
    return RuleRunStarted(
        run_id=result.run_id,
        scope=result.scope,
        status="completed",
        totals=totals,
    )


@router.get(
    "/rules/runs/{run_id}/findings",
    response_model=RunFindingsOut,
    dependencies=[DenyCurator],
)
def get_run_findings(
    run_id: uuid.UUID, db: DbDep, group_by: GroupByQuery = None, limit: LimitQuery = 200
) -> RunFindingsOut:
    """Findings of a run: per-rule groups + case-level rows. Curator: 403 (case-level)."""
    severity_by_code = {
        code: severity
        for code, severity in db.execute(sa.select(Rule.code, Rule.severity)).all()
    }
    grouped = db.execute(
        sa.select(
            Finding.rule_code,
            sa.func.count().label("count"),
            sa.func.coalesce(sa.func.sum(Finding.amount_at_risk), 0).label("amount"),
        )
        .where(Finding.run_id == run_id)
        .group_by(Finding.rule_code)
        .order_by(Finding.rule_code)
    ).all()
    groups = [
        FindingGroupOut(
            rule_code=g.rule_code,
            severity=severity_by_code.get(g.rule_code),
            count=int(g.count),
            amount_at_risk=int(g.amount),
        )
        for g in grouped
    ]
    findings = [
        FindingOut.model_validate(f)
        for f in db.execute(
            sa.select(Finding)
            .where(Finding.run_id == run_id)
            .order_by(Finding.rule_code, Finding.amount_at_risk.desc())
            .limit(limit)
        ).scalars()
    ]
    return RunFindingsOut(run_id=run_id, group_by=group_by, groups=groups, findings=findings)


@router.patch("/findings/{finding_id}", response_model=FindingOut, dependencies=[DenyCurator])
def patch_finding(
    finding_id: uuid.UUID, body: FindingPatch, db: DbDep, principal: OptionalPrincipal
) -> FindingOut:
    """Exclude a finding from the registry or dismiss it (docs/04 GUARD). Curator: 403."""
    finding = db.get(Finding, finding_id)
    if finding is None:
        raise HTTPException(status_code=404, detail="finding not found")
    finding.status = FindingStatus(body.status)
    if body.comment:
        details = dict(finding.details or {})
        details["comment"] = body.comment
        finding.details = details
    if finding.status in (FindingStatus.excluded, FindingStatus.dismissed):
        events_svc.finding_status_changed(
            db, principal, finding_id=str(finding.id), rule_code=finding.rule_code,
            ekd_code=(finding.details or {}).get("ekd_code"),
            amount=int(finding.amount_at_risk), status=finding.status.value,
        )
    db.commit()
    db.refresh(finding)
    return FindingOut.model_validate(finding)
