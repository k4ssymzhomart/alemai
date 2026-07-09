"""SQLAlchemy 2.0 models — one class per table in docs/05 §4.

Importing this package registers every table on ``app.db.Base.metadata``.
"""

from app.models.alerts import Alert, Deadline
from app.models.analytics import Forecast, RiskAssessment
from app.models.claim import Claim
from app.models.contract import Contract, ContractLine, ContractVersion
from app.models.events import AppConfig, Event, RadarCheck
from app.models.imports import ImportFile, QuarantineRow
from app.models.org import Organization
from app.models.people import Doctor, Patient
from app.models.reference import PackageMapping, RegChunk, RegDocument
from app.models.rules import Finding, Rule, RuleRun
from app.models.users import AuditLog, User

__all__ = [
    "Alert",
    "AppConfig",
    "AuditLog",
    "Claim",
    "Contract",
    "ContractLine",
    "ContractVersion",
    "Deadline",
    "Event",
    "Doctor",
    "Finding",
    "Forecast",
    "ImportFile",
    "Organization",
    "PackageMapping",
    "Patient",
    "QuarantineRow",
    "RadarCheck",
    "RegChunk",
    "RegDocument",
    "RiskAssessment",
    "Rule",
    "RuleRun",
    "User",
]
