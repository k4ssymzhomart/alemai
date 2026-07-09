"""Ops dashboard API schemas (EPIC G4)."""

from app.schemas.common import APIModel


class CounterOut(APIModel):
    key: str
    count: int


class RefVersionOut(APIModel):
    key: str
    label: str
    version: str


class OpsDashboardOut(APIModel):
    registries_checked: int
    positions_scanned: int
    findings_total: int
    findings_by_severity: list[CounterOut]
    sanctions_prevented_tenge: int
    objections_filed: int
    documents_generated: int
    documents_by_kind: list[CounterOut]
    reconcile_cases: int
    reconcile_tenge: int
    imports_count: int
    import_rows_ok: int
    import_rows_quarantined: int
    active_users: int
    events_total: int
    last_demo_reset: str | None = None
    app_version: str
    ref_versions: list[RefVersionOut]
