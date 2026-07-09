"""Ops dashboard aggregation (EPIC G4) — every counter from a real DB query.

Answers «сколько реестров проверено / документов сравнили / санкций
предотвращено» with live numbers, not slideware. Counters clear after a
demo-reset (events/findings/runs are truncated), so the panel reflects the
current session's activity.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.events import Event
from app.models.imports import ImportFile
from app.models.rules import Finding, Rule, RuleRun
from app.services import reconcile as reconcile_svc
from app.services.config import LAST_DEMO_RESET_KEY, get_config
from app.services.rules_engine import ekd

APP_VERSION = "QALAM · 0.5 · demo"

# Reference-data versions (trust signal, docs/13 §4.12). key → (label_ru, version).
REF_VERSIONS: list[tuple[str, str, str]] = [
    ("ekd", "ЕКД (классификатор дефектов)", "ред. приказа №19 · 27.02.2026"),
    ("tarif", "Тарификатор", "№ ҚР ДСМ-170/2020 · прил. 7"),
    ("packages", "Пакеты ГОБМП/ОСМС", "ПП №672 / №421 · 2026"),
    ("payment", "Правила оплаты", "№ ҚР ДСМ-291/2020 · ред. 18.05.2026"),
    ("monitoring", "Правила мониторинга", "№ ҚР ДСМ-321/2020 · ред. 27.02.2026"),
]


@dataclass(frozen=True, slots=True)
class Counter:
    key: str
    count: int


@dataclass(slots=True)
class OpsDashboard:
    registries_checked: int
    positions_scanned: int
    findings_total: int
    findings_by_severity: list[Counter]
    sanctions_prevented_tenge: int
    objections_filed: int
    documents_generated: int
    documents_by_kind: list[Counter]
    reconcile_cases: int
    reconcile_tenge: int
    imports_count: int
    import_rows_ok: int
    import_rows_quarantined: int
    active_users: int
    events_total: int
    last_demo_reset: str | None
    app_version: str
    ref_versions: list[dict[str, str]] = field(default_factory=list)


def dashboard(db: Session) -> OpsDashboard:
    kpn = get_settings().kpn_tenge

    registries_checked = int(
        db.execute(sa.select(sa.func.count()).select_from(RuleRun)).scalar_one()
    )
    # Positions scanned = the latest check's coverage (stable across re-runs).
    latest_totals = db.execute(
        sa.select(RuleRun.totals).order_by(RuleRun.started_at.desc()).limit(1)
    ).scalar_one_or_none()
    positions_scanned = int((latest_totals or {}).get("claims_scanned", 0))

    # Defect counts dedupe by (claim, rule): re-running the check must not double
    # the "всего дефектов" number.
    distinct_findings = (
        sa.select(Finding.claim_id, Finding.rule_code, Rule.severity.label("severity"))
        .join(Rule, Rule.code == Finding.rule_code)
        .distinct()
        .subquery()
    )
    findings_total = int(
        db.execute(sa.select(sa.func.count()).select_from(distinct_findings)).scalar_one()
    )
    findings_by_severity = [
        Counter(str(s), int(c))
        for s, c in db.execute(
            sa.select(distinct_findings.c.severity, sa.func.count())
            .group_by(distinct_findings.c.severity)
        ).all()
    ]

    # Sanctions prevented = full ЕКД penalty of findings EXCLUDED before billing,
    # deduped by (claim, rule) so a re-exclude across runs counts once.
    sanctions_prevented = 0
    for details in db.execute(
        sa.select(Finding.details)
        .distinct(Finding.claim_id, Finding.rule_code)
        .where(Finding.status == "excluded")
        .order_by(Finding.claim_id, Finding.rule_code)
    ).scalars():
        d = details or {}
        code, care_type = d.get("ekd_code"), d.get("care_type")
        billed = int(d.get("amount_billed") or 0)
        if code and care_type:
            sanctions_prevented += ekd.sanction_total(code, str(care_type), billed, kpn)

    objections_filed = int(
        db.execute(
            sa.select(sa.func.count()).select_from(Event)
            .where(Event.type == "objection_filed")
        ).scalar_one()
    )
    documents_by_kind = [
        Counter(str(k or "—"), int(c))
        for k, c in db.execute(
            sa.select(Event.payload["kind"].astext.label("kind"), sa.func.count())
            .where(Event.type == "document_generated")
            .group_by(sa.literal_column("1"))  # ordinal — the JSONB path binds once
        ).all()
    ]
    documents_generated = sum(c.count for c in documents_by_kind)

    bucket1 = next((b for b in reconcile_svc.buckets(db) if b.bucket_no == 1), None)

    imp = db.execute(
        sa.select(
            sa.func.count(),
            sa.func.coalesce(sa.func.sum(ImportFile.rows_ok), 0),
            sa.func.coalesce(sa.func.sum(ImportFile.rows_quarantined), 0),
        )
    ).one()

    active_users = int(
        db.execute(
            sa.select(sa.func.count(sa.distinct(Event.actor_username)))
            .where(Event.actor_username.isnot(None))
        ).scalar_one()
    )
    events_total = int(
        db.execute(sa.select(sa.func.count()).select_from(Event)).scalar_one()
    )

    reset = get_config(db, LAST_DEMO_RESET_KEY, {})

    return OpsDashboard(
        registries_checked=registries_checked,
        positions_scanned=positions_scanned,
        findings_total=findings_total,
        findings_by_severity=findings_by_severity,
        sanctions_prevented_tenge=int(sanctions_prevented),
        objections_filed=objections_filed,
        documents_generated=documents_generated,
        documents_by_kind=documents_by_kind,
        reconcile_cases=bucket1.rows_count if bucket1 else 0,
        reconcile_tenge=bucket1.total_amount if bucket1 else 0,
        imports_count=int(imp[0]),
        import_rows_ok=int(imp[1]),
        import_rows_quarantined=int(imp[2]),
        active_users=active_users,
        events_total=events_total,
        last_demo_reset=reset.get("at"),
        app_version=APP_VERSION,
        ref_versions=[{"key": k, "label": lbl, "version": v} for k, lbl, v in REF_VERSIONS],
    )
