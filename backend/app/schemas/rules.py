"""Rules engine API schemas (docs/05 §5, docs/06 §7)."""

import uuid
from typing import Any, Literal

from pydantic import Field

from app.models.enums import FindingStatus, RuleSeverity
from app.schemas.common import APIModel


class RuleOut(APIModel):
    code: str
    severity: RuleSeverity
    scope: str
    enabled: bool = True
    params: dict[str, Any] | None = None
    message_kk: str
    message_ru: str
    origin: str


class RuleRunIn(APIModel):
    scope: str = Field(description="e.g. 'all', 'period:2026-11', 'import:<file_id>'")


class RuleRunStarted(APIModel):
    run_id: uuid.UUID
    scope: str
    status: str = "started"


class FindingOut(APIModel):
    id: uuid.UUID
    run_id: uuid.UUID
    rule_code: str
    claim_id: uuid.UUID | None = None
    amount_at_risk: int = Field(default=0, description="whole tenge")
    details: dict[str, Any] | None = None
    status: FindingStatus = FindingStatus.open


class FindingGroupOut(APIModel):
    rule_code: str
    severity: RuleSeverity | None = None
    count: int = 0
    amount_at_risk: int = Field(default=0, description="whole tenge")


class RunFindingsOut(APIModel):
    run_id: uuid.UUID
    group_by: str | None = None
    groups: list[FindingGroupOut] = []
    findings: list[FindingOut] = []


class FindingPatch(APIModel):
    """PATCH /findings/{id}: exclude from registry or dismiss (docs/04 GUARD)."""

    status: Literal["excluded", "dismissed", "fixed", "open"]
    comment: str | None = None
