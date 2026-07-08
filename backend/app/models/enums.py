"""Domain enums (docs/05 §4, docs/03 D2, docs/06 §6-§7).

All enums are plain ``str`` enums and are stored in PostgreSQL as text
(``sqlalchemy.Enum(native_enum=False)`` — see :func:`text_enum`).
"""

import enum

from sqlalchemy import Enum as SAEnum


class OrgType(enum.StrEnum):
    polyclinic = "polyclinic"
    hospital = "hospital"


class ContractStatus(enum.StrEnum):
    draft = "draft"
    active = "active"
    closed = "closed"


class CareType(enum.StrEnum):
    pmsp = "pmsp"
    kdu = "kdu"
    day_hosp = "day_hosp"
    hosp = "hosp"
    dent = "dent"
    screening = "screening"
    ambulance = "ambulance"


class FundingSource(enum.StrEnum):
    gobmp = "gobmp"
    osms = "osms"


class Sex(enum.StrEnum):
    male = "M"
    female = "F"


class ClaimStatus(enum.StrEnum):
    mis_only = "mis_only"
    submitted = "submitted"
    accepted = "accepted"
    rejected = "rejected"
    paid = "paid"


class ImportKind(enum.StrEnum):
    contract = "contract"
    amendment = "amendment"
    mis = "mis"
    fund_statement = "fund_statement"
    rpn = "rpn"


class RuleSeverity(enum.StrEnum):
    block = "block"  # exclude from the счёт-реестр (would be rejected pre-billing)
    warn = "warn"  # review — probable defect, not an automatic block
    info = "info"
    yellow = "yellow"  # ЕКД 2.0/7.0 — фиксируется без снятия (0 ₸), a soft flag


class FindingStatus(enum.StrEnum):
    open = "open"
    excluded = "excluded"
    fixed = "fixed"
    dismissed = "dismissed"


class ForecastMethod(enum.StrEnum):
    """docs/06 §6: run-rate, Holt-Winters, or their 50/50 ensemble."""

    runrate = "runrate"
    holt_winters = "holt_winters"
    ensemble = "ensemble"


class RiskClass(enum.StrEnum):
    """docs/03 D2: thresholds on projected year-end gap (configurable)."""

    critical_under = "critical_under"  # < -10%
    under_risk = "under_risk"  # -10% .. -5%
    on_track = "on_track"  # +-5%
    over_risk = "over_risk"  # +5% .. +10%
    critical_over = "critical_over"  # > +10%


class AlertSeverity(enum.StrEnum):
    info = "info"
    warn = "warn"
    critical = "critical"


class AlertStatus(enum.StrEnum):
    active = "active"
    acknowledged = "acknowledged"
    resolved = "resolved"


class DeadlineKind(enum.StrEnum):
    korrektirovka_window = "korrektirovka_window"
    invoice_due = "invoice_due"
    report_due = "report_due"


class UserRole(enum.StrEnum):
    """docs/04 §1 RBAC — four hackathon roles plus admin."""

    economist = "economist"
    statistician = "statistician"
    chief = "chief"
    curator = "curator"
    admin = "admin"


def text_enum(enum_cls: type[enum.Enum], length: int = 32) -> SAEnum:
    """Column type storing a Python str enum as plain text (no native PG enum)."""
    return SAEnum(
        enum_cls,
        native_enum=False,
        validate_strings=True,
        length=length,
        values_callable=lambda e: [m.value for m in e],
    )
