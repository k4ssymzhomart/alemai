"""Rules engine endpoints (docs/05 §5). Includes PATCH /findings/{id}."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Query

from app.models.enums import FindingStatus
from app.schemas.rules import FindingOut, FindingPatch, RuleRunIn, RuleRunStarted, RunFindingsOut

router = APIRouter(tags=["rules"])

GroupByQuery = Annotated[str | None, Query(description="e.g. 'rule'")]


@router.post("/rules/run", response_model=RuleRunStarted, status_code=202)
def run_rules(body: RuleRunIn) -> RuleRunStarted:
    """Start a rules run over the given scope. Stub: returns a run id, no work."""
    return RuleRunStarted(run_id=uuid.uuid4(), scope=body.scope, status="started")


@router.get("/rules/runs/{run_id}/findings", response_model=RunFindingsOut)
def get_run_findings(run_id: uuid.UUID, group_by: GroupByQuery = None) -> RunFindingsOut:
    """Findings of a run, optionally grouped by rule."""
    return RunFindingsOut(run_id=run_id, group_by=group_by, groups=[], findings=[])


@router.patch("/findings/{finding_id}", response_model=FindingOut)
def patch_finding(finding_id: uuid.UUID, body: FindingPatch) -> FindingOut:
    """Exclude a finding from the registry or dismiss it. Stub: echoes new status."""
    return FindingOut(
        id=finding_id,
        run_id=uuid.uuid4(),
        rule_code="R00",
        claim_id=None,
        amount_at_risk=0,
        details={"comment": body.comment} if body.comment else None,
        status=FindingStatus(body.status),
    )
