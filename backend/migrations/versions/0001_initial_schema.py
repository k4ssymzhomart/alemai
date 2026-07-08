"""initial schema — pgvector extension, all 21 model tables (docs/05 §4),
service_group_map auxiliary table, hot-path indexes and the mv_line_execution
materialized view (shared contract C2).

Revision ID: 0001
Revises:
Create Date: 2026-07-08

"""

from collections.abc import Sequence

import pgvector.sqlalchemy
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# fact = accepted+paid; billed adds submitted; rejected/paid/mis_only by status.
# contract_lines.month and claims.period are both 'YYYY-MM' strings; the MV
# exposes month (int 1-12) and period (text) per shared contract C2.
MV_LINE_EXECUTION_SQL = """
CREATE MATERIALIZED VIEW mv_line_execution AS
WITH plan AS (
    SELECT
        cl.contract_id,
        c.org_id,
        c.year,
        cl.care_type::text              AS care_type,
        cl.funding_source::text         AS funding_source,
        COALESCE(cl.service_group, '')  AS service_group,
        cl.month                        AS period,
        SUM(cl.plan_qty)::bigint        AS plan_qty,
        SUM(cl.plan_amount)::bigint     AS plan_amount
    FROM contract_lines cl
    JOIN contracts c ON c.id = cl.contract_id
    GROUP BY cl.contract_id, c.org_id, c.year, cl.care_type::text,
             cl.funding_source::text, COALESCE(cl.service_group, ''), cl.month
),
fact AS (
    SELECT
        ct.id                           AS contract_id,
        cm.org_id,
        cm.care_type::text              AS care_type,
        cm.funding_source::text         AS funding_source,
        COALESCE(sgm.service_group, '') AS service_group,
        cm.period,
        COALESCE(SUM(cm.qty)    FILTER (WHERE cm.status IN ('accepted', 'paid')),
                 0)::bigint AS fact_qty,
        COALESCE(SUM(cm.amount) FILTER (WHERE cm.status IN ('accepted', 'paid')),
                 0)::bigint AS fact_amount,
        COALESCE(SUM(cm.qty)    FILTER (WHERE cm.status IN ('submitted', 'accepted', 'paid')),
                 0)::bigint AS billed_qty,
        COALESCE(SUM(cm.amount) FILTER (WHERE cm.status IN ('submitted', 'accepted', 'paid')),
                 0)::bigint AS billed_amount,
        COALESCE(SUM(cm.qty)    FILTER (WHERE cm.status = 'rejected'), 0)::bigint AS rejected_qty,
        COALESCE(SUM(cm.amount) FILTER (WHERE cm.status = 'rejected'), 0)::bigint
            AS rejected_amount,
        COALESCE(SUM(cm.qty)    FILTER (WHERE cm.status = 'paid'), 0)::bigint AS paid_qty,
        COALESCE(SUM(cm.amount) FILTER (WHERE cm.status = 'paid'), 0)::bigint AS paid_amount,
        COALESCE(SUM(cm.qty)    FILTER (WHERE cm.status = 'mis_only'), 0)::bigint AS mis_only_qty,
        COALESCE(SUM(cm.amount) FILTER (WHERE cm.status = 'mis_only'), 0)::bigint
            AS mis_only_amount
    FROM claims cm
    LEFT JOIN service_group_map sgm ON sgm.service_code = cm.service_code
    LEFT JOIN contracts ct
           ON ct.org_id = cm.org_id
          AND ct.year = CAST(LEFT(cm.period, 4) AS int)
    GROUP BY ct.id, cm.org_id, cm.care_type::text, cm.funding_source::text,
             COALESCE(sgm.service_group, ''), cm.period
)
SELECT
    COALESCE(p.contract_id, f.contract_id)              AS contract_id,
    COALESCE(p.org_id, f.org_id)                        AS org_id,
    COALESCE(p.year, CAST(LEFT(f.period, 4) AS int))    AS year,
    COALESCE(p.care_type, f.care_type)                  AS care_type,
    COALESCE(p.funding_source, f.funding_source)        AS funding_source,
    COALESCE(p.service_group, f.service_group)          AS service_group,
    CAST(RIGHT(COALESCE(p.period, f.period), 2) AS int) AS month,
    COALESCE(p.period, f.period)                        AS period,
    COALESCE(p.plan_qty, 0)                             AS plan_qty,
    COALESCE(p.plan_amount, 0)                          AS plan_amount,
    COALESCE(f.fact_qty, 0)                             AS fact_qty,
    COALESCE(f.fact_amount, 0)                          AS fact_amount,
    COALESCE(f.billed_qty, 0)                           AS billed_qty,
    COALESCE(f.billed_amount, 0)                        AS billed_amount,
    COALESCE(f.rejected_qty, 0)                         AS rejected_qty,
    COALESCE(f.rejected_amount, 0)                      AS rejected_amount,
    COALESCE(f.paid_qty, 0)                             AS paid_qty,
    COALESCE(f.paid_amount, 0)                          AS paid_amount,
    COALESCE(f.mis_only_qty, 0)                         AS mis_only_qty,
    COALESCE(f.mis_only_amount, 0)                      AS mis_only_amount
FROM plan p
FULL OUTER JOIN fact f
       ON f.org_id = p.org_id
      AND f.care_type = p.care_type
      AND f.funding_source = p.funding_source
      AND f.service_group = p.service_group
      AND f.period = p.period
"""


def upgrade() -> None:
    # pgvector must exist before reg_chunks.embedding (vector(1024)) is created.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "alerts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column(
            "severity",
            sa.Enum("info", "warn", "critical", name="alertseverity", native_enum=False, length=32),
            nullable=False,
        ),
        sa.Column("title_kk", sa.String(length=255), nullable=False),
        sa.Column("title_ru", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.BigInteger(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("entity_ref", sa.String(length=128), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "acknowledged",
                "resolved",
                name="alertstatus",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_alerts")),
    )
    op.create_index(op.f("ix_alerts_status"), "alerts", ["status"], unique=False)
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("who", sa.String(length=128), nullable=False),
        sa.Column("what", sa.Text(), nullable=False),
        sa.Column("when", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_log")),
    )
    op.create_table(
        "deadlines",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "kind",
            sa.Enum(
                "korrektirovka_window",
                "invoice_due",
                "report_due",
                name="deadlinekind",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("starts", sa.Date(), nullable=False),
        sa.Column("ends", sa.Date(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_deadlines")),
    )
    op.create_table(
        "import_files",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "kind",
            sa.Enum(
                "contract",
                "amendment",
                "mis",
                "fund_statement",
                "rpn",
                name="importkind",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("rows_ok", sa.Integer(), nullable=False),
        sa.Column("rows_quarantined", sa.Integer(), nullable=False),
        sa.Column("control_sum", sa.BigInteger(), nullable=True),
        sa.Column("loaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_import_files")),
    )
    op.create_table(
        "organizations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name_kk", sa.String(length=255), nullable=False),
        sa.Column("name_ru", sa.String(length=255), nullable=False),
        sa.Column(
            "type",
            sa.Enum("polyclinic", "hospital", name="orgtype", native_enum=False, length=32),
            nullable=False,
        ),
        sa.Column("attached_population", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_organizations")),
    )
    op.create_table(
        "package_mapping",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("icd10", sa.String(length=16), nullable=True),
        sa.Column("service_code", sa.String(length=64), nullable=True),
        sa.Column(
            "funding_source",
            sa.Enum("gobmp", "osms", name="fundingsource", native_enum=False, length=32),
            nullable=False,
        ),
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_package_mapping")),
    )
    op.create_index(op.f("ix_package_mapping_icd10"), "package_mapping", ["icd10"], unique=False)
    op.create_index(
        op.f("ix_package_mapping_service_code"), "package_mapping", ["service_code"], unique=False
    )
    op.create_table(
        "patients",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("sex", sa.Enum("M", "F", name="sex", native_enum=False), nullable=False),
        sa.Column("birth_year", sa.Integer(), nullable=False),
        sa.Column("attached", sa.Boolean(), nullable=False),
        sa.Column("insured", sa.Boolean(), nullable=False),
        sa.Column("death_date", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_patients")),
    )
    op.create_table(
        "reg_documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("number", sa.String(length=64), nullable=False),
        sa.Column("lang", sa.String(length=2), nullable=False),
        sa.Column("url", sa.String(length=512), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reg_documents")),
    )
    op.create_table(
        "rule_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("scope", sa.String(length=64), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("totals", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rule_runs")),
    )
    op.create_table(
        "rules",
        sa.Column("code", sa.String(length=8), nullable=False),
        sa.Column(
            "severity",
            sa.Enum("block", "warn", "info", name="ruleseverity", native_enum=False, length=32),
            nullable=False,
        ),
        sa.Column("scope", sa.String(length=32), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("params", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("message_kk", sa.Text(), nullable=False),
        sa.Column("message_ru", sa.Text(), nullable=False),
        sa.Column("origin", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("code", name=op.f("pk_rules")),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "economist",
                "statistician",
                "chief",
                "curator",
                "admin",
                name="userrole",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_table(
        "contracts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("org_id", sa.Uuid(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("number", sa.String(length=64), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "draft", "active", "closed", name="contractstatus", native_enum=False, length=32
            ),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["org_id"], ["organizations.id"], name=op.f("fk_contracts_org_id_organizations")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_contracts")),
    )
    op.create_index(op.f("ix_contracts_org_id"), "contracts", ["org_id"], unique=False)
    op.create_table(
        "doctors",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("org_id", sa.Uuid(), nullable=False),
        sa.Column("full_name_masked", sa.String(length=128), nullable=False),
        sa.Column("specialty", sa.String(length=128), nullable=False),
        sa.Column("dept", sa.String(length=128), nullable=False),
        sa.Column("schedule_ref", sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(
            ["org_id"], ["organizations.id"], name=op.f("fk_doctors_org_id_organizations")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_doctors")),
    )
    op.create_index(op.f("ix_doctors_org_id"), "doctors", ["org_id"], unique=False)
    op.create_table(
        "quarantine_rows",
        sa.Column("import_file_id", sa.Uuid(), nullable=False),
        sa.Column("row_no", sa.Integer(), nullable=False),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("errors", sa.ARRAY(sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(
            ["import_file_id"],
            ["import_files.id"],
            name=op.f("fk_quarantine_rows_import_file_id_import_files"),
        ),
        sa.PrimaryKeyConstraint("import_file_id", "row_no", name=op.f("pk_quarantine_rows")),
    )
    op.create_table(
        "reg_chunks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("doc_id", sa.Uuid(), nullable=False),
        sa.Column("anchor", sa.String(length=128), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("embedding", pgvector.sqlalchemy.vector.VECTOR(dim=1024), nullable=True),
        sa.ForeignKeyConstraint(
            ["doc_id"], ["reg_documents.id"], name=op.f("fk_reg_chunks_doc_id_reg_documents")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reg_chunks")),
    )
    op.create_index(op.f("ix_reg_chunks_doc_id"), "reg_chunks", ["doc_id"], unique=False)
    op.create_table(
        "claims",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("org_id", sa.Uuid(), nullable=False),
        sa.Column("patient_id", sa.String(length=64), nullable=False),
        sa.Column("doctor_id", sa.Uuid(), nullable=False),
        sa.Column("dept", sa.String(length=128), nullable=False),
        sa.Column(
            "care_type",
            sa.Enum(
                "pmsp",
                "kdu",
                "day_hosp",
                "hosp",
                "dent",
                "screening",
                "ambulance",
                name="caretype",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "funding_source",
            sa.Enum("gobmp", "osms", name="fundingsource", native_enum=False, length=32),
            nullable=False,
        ),
        sa.Column("service_code", sa.String(length=64), nullable=False),
        sa.Column("service_name", sa.String(length=255), nullable=False),
        sa.Column("icd10", sa.String(length=16), nullable=True),
        sa.Column("date_start", sa.Date(), nullable=False),
        sa.Column("date_end", sa.Date(), nullable=True),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("tariff", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.BigInteger(), nullable=False),
        sa.Column("referral_id", sa.String(length=64), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "mis_only",
                "submitted",
                "accepted",
                "rejected",
                "paid",
                name="claimstatus",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("period", sa.String(length=7), nullable=False),
        sa.Column("source_file_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["doctor_id"], ["doctors.id"], name=op.f("fk_claims_doctor_id_doctors")
        ),
        sa.ForeignKeyConstraint(
            ["org_id"], ["organizations.id"], name=op.f("fk_claims_org_id_organizations")
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"], ["patients.id"], name=op.f("fk_claims_patient_id_patients")
        ),
        sa.ForeignKeyConstraint(
            ["source_file_id"],
            ["import_files.id"],
            name=op.f("fk_claims_source_file_id_import_files"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_claims")),
    )
    op.create_index(op.f("ix_claims_care_type"), "claims", ["care_type"], unique=False)
    op.create_index(op.f("ix_claims_date_start"), "claims", ["date_start"], unique=False)
    op.create_index(op.f("ix_claims_doctor_id"), "claims", ["doctor_id"], unique=False)
    op.create_index(op.f("ix_claims_funding_source"), "claims", ["funding_source"], unique=False)
    op.create_index(op.f("ix_claims_org_id"), "claims", ["org_id"], unique=False)
    op.create_index(op.f("ix_claims_patient_id"), "claims", ["patient_id"], unique=False)
    op.create_index(op.f("ix_claims_period"), "claims", ["period"], unique=False)
    op.create_index(op.f("ix_claims_service_code"), "claims", ["service_code"], unique=False)
    op.create_index(op.f("ix_claims_status"), "claims", ["status"], unique=False)
    op.create_table(
        "contract_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("contract_id", sa.Uuid(), nullable=False),
        sa.Column("amendment_no", sa.Integer(), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["contract_id"],
            ["contracts.id"],
            name=op.f("fk_contract_versions_contract_id_contracts"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_contract_versions")),
    )
    op.create_index(
        op.f("ix_contract_versions_contract_id"), "contract_versions", ["contract_id"], unique=False
    )
    op.create_table(
        "forecasts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("contract_id", sa.Uuid(), nullable=False),
        sa.Column(
            "care_type",
            sa.Enum(
                "pmsp",
                "kdu",
                "day_hosp",
                "hosp",
                "dent",
                "screening",
                "ambulance",
                name="caretype",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "funding_source",
            sa.Enum("gobmp", "osms", name="fundingsource", native_enum=False, length=32),
            nullable=False,
        ),
        sa.Column("service_group", sa.String(length=128), nullable=True),
        sa.Column("as_of", sa.Date(), nullable=False),
        sa.Column("horizon_month", sa.String(length=7), nullable=False),
        sa.Column(
            "method",
            sa.Enum(
                "runrate",
                "holt_winters",
                "ensemble",
                name="forecastmethod",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("value_qty", sa.Integer(), nullable=False),
        sa.Column("value_amount", sa.BigInteger(), nullable=False),
        sa.Column("ci_low", sa.BigInteger(), nullable=False),
        sa.Column("ci_high", sa.BigInteger(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("inputs_hash", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(
            ["contract_id"], ["contracts.id"], name=op.f("fk_forecasts_contract_id_contracts")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_forecasts")),
    )
    op.create_index(op.f("ix_forecasts_as_of"), "forecasts", ["as_of"], unique=False)
    op.create_index(op.f("ix_forecasts_care_type"), "forecasts", ["care_type"], unique=False)
    op.create_index(op.f("ix_forecasts_contract_id"), "forecasts", ["contract_id"], unique=False)
    op.create_index(
        op.f("ix_forecasts_funding_source"), "forecasts", ["funding_source"], unique=False
    )
    op.create_table(
        "risk_assessments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("contract_id", sa.Uuid(), nullable=False),
        sa.Column(
            "care_type",
            sa.Enum(
                "pmsp",
                "kdu",
                "day_hosp",
                "hosp",
                "dent",
                "screening",
                "ambulance",
                name="caretype",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "funding_source",
            sa.Enum("gobmp", "osms", name="fundingsource", native_enum=False, length=32),
            nullable=False,
        ),
        sa.Column("service_group", sa.String(length=128), nullable=True),
        sa.Column("as_of", sa.Date(), nullable=False),
        sa.Column(
            "class",
            sa.Enum(
                "critical_under",
                "under_risk",
                "on_track",
                "over_risk",
                "critical_over",
                name="riskclass",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("gap_amount", sa.BigInteger(), nullable=False),
        sa.Column("burn_out_date", sa.Date(), nullable=True),
        sa.Column("recommendation", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(
            ["contract_id"],
            ["contracts.id"],
            name=op.f("fk_risk_assessments_contract_id_contracts"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_risk_assessments")),
    )
    op.create_index(op.f("ix_risk_assessments_as_of"), "risk_assessments", ["as_of"], unique=False)
    op.create_index(
        op.f("ix_risk_assessments_care_type"), "risk_assessments", ["care_type"], unique=False
    )
    op.create_index(op.f("ix_risk_assessments_class"), "risk_assessments", ["class"], unique=False)
    op.create_index(
        op.f("ix_risk_assessments_contract_id"), "risk_assessments", ["contract_id"], unique=False
    )
    op.create_index(
        op.f("ix_risk_assessments_funding_source"),
        "risk_assessments",
        ["funding_source"],
        unique=False,
    )
    op.create_table(
        "contract_lines",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("contract_id", sa.Uuid(), nullable=False),
        sa.Column(
            "care_type",
            sa.Enum(
                "pmsp",
                "kdu",
                "day_hosp",
                "hosp",
                "dent",
                "screening",
                "ambulance",
                name="caretype",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "funding_source",
            sa.Enum("gobmp", "osms", name="fundingsource", native_enum=False, length=32),
            nullable=False,
        ),
        sa.Column("service_group", sa.String(length=128), nullable=True),
        sa.Column("month", sa.String(length=7), nullable=False),
        sa.Column("plan_qty", sa.Integer(), nullable=False),
        sa.Column("plan_amount", sa.BigInteger(), nullable=False),
        sa.Column("version_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["contract_id"], ["contracts.id"], name=op.f("fk_contract_lines_contract_id_contracts")
        ),
        sa.ForeignKeyConstraint(
            ["version_id"],
            ["contract_versions.id"],
            name=op.f("fk_contract_lines_version_id_contract_versions"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_contract_lines")),
    )
    op.create_index(
        op.f("ix_contract_lines_contract_id"), "contract_lines", ["contract_id"], unique=False
    )
    op.create_index(
        op.f("ix_contract_lines_version_id"), "contract_lines", ["version_id"], unique=False
    )
    op.create_table(
        "findings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("rule_code", sa.String(length=8), nullable=False),
        sa.Column("claim_id", sa.Uuid(), nullable=True),
        sa.Column("amount_at_risk", sa.BigInteger(), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "open",
                "excluded",
                "fixed",
                "dismissed",
                name="findingstatus",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["claim_id"], ["claims.id"], name=op.f("fk_findings_claim_id_claims")
        ),
        sa.ForeignKeyConstraint(
            ["rule_code"], ["rules.code"], name=op.f("fk_findings_rule_code_rules")
        ),
        sa.ForeignKeyConstraint(
            ["run_id"], ["rule_runs.id"], name=op.f("fk_findings_run_id_rule_runs")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_findings")),
    )
    op.create_index(op.f("ix_findings_claim_id"), "findings", ["claim_id"], unique=False)
    op.create_index(op.f("ix_findings_rule_code"), "findings", ["rule_code"], unique=False)
    op.create_index(op.f("ix_findings_run_id"), "findings", ["run_id"], unique=False)
    op.create_index(op.f("ix_findings_status"), "findings", ["status"], unique=False)
    # ### end Alembic commands ###

    # --- auxiliary table (not in models metadata; owned by this migration) ---
    # service_code -> service_group resolution for claims (contract C2).
    # Empty in P1; P3 fills it for the МРТ/stomatology storylines.
    op.create_table(
        "service_group_map",
        sa.Column("service_code", sa.Text(), nullable=False),
        sa.Column("service_group", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("service_code", name=op.f("pk_service_group_map")),
    )

    # --- hot-path composite indexes (claim->line mapping, monthly drill-down) ---
    op.create_index(
        "ix_claims_org_care_source_period",
        "claims",
        ["org_id", "care_type", "funding_source", "period"],
        unique=False,
    )
    op.create_index(
        "ix_contract_lines_contract_month",
        "contract_lines",
        ["contract_id", "month"],
        unique=False,
    )

    # --- mv_line_execution (contract C2) -------------------------------------
    # Grain: (contract_id, care_type, funding_source, service_group, month).
    # FULL OUTER JOIN keeps claims without a plan line (plan_* = 0) and plan
    # lines without claims (fact_* = 0). service_group resolves through
    # service_group_map (LEFT JOIN, COALESCE to '').
    op.execute(MV_LINE_EXECUTION_SQL)
    op.execute(
        """
        CREATE UNIQUE INDEX ix_mv_line_execution_grain
            ON mv_line_execution
            (contract_id, care_type, funding_source, service_group, period)
        """
    )
    op.execute("CREATE INDEX ix_mv_line_execution_year ON mv_line_execution (year)")


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_line_execution")
    op.drop_index("ix_contract_lines_contract_month", table_name="contract_lines")
    op.drop_index("ix_claims_org_care_source_period", table_name="claims")
    op.drop_table("service_group_map")
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_findings_status"), table_name="findings")
    op.drop_index(op.f("ix_findings_run_id"), table_name="findings")
    op.drop_index(op.f("ix_findings_rule_code"), table_name="findings")
    op.drop_index(op.f("ix_findings_claim_id"), table_name="findings")
    op.drop_table("findings")
    op.drop_index(op.f("ix_contract_lines_version_id"), table_name="contract_lines")
    op.drop_index(op.f("ix_contract_lines_contract_id"), table_name="contract_lines")
    op.drop_table("contract_lines")
    op.drop_index(op.f("ix_risk_assessments_funding_source"), table_name="risk_assessments")
    op.drop_index(op.f("ix_risk_assessments_contract_id"), table_name="risk_assessments")
    op.drop_index(op.f("ix_risk_assessments_class"), table_name="risk_assessments")
    op.drop_index(op.f("ix_risk_assessments_care_type"), table_name="risk_assessments")
    op.drop_index(op.f("ix_risk_assessments_as_of"), table_name="risk_assessments")
    op.drop_table("risk_assessments")
    op.drop_index(op.f("ix_forecasts_funding_source"), table_name="forecasts")
    op.drop_index(op.f("ix_forecasts_contract_id"), table_name="forecasts")
    op.drop_index(op.f("ix_forecasts_care_type"), table_name="forecasts")
    op.drop_index(op.f("ix_forecasts_as_of"), table_name="forecasts")
    op.drop_table("forecasts")
    op.drop_index(op.f("ix_contract_versions_contract_id"), table_name="contract_versions")
    op.drop_table("contract_versions")
    op.drop_index(op.f("ix_claims_status"), table_name="claims")
    op.drop_index(op.f("ix_claims_service_code"), table_name="claims")
    op.drop_index(op.f("ix_claims_period"), table_name="claims")
    op.drop_index(op.f("ix_claims_patient_id"), table_name="claims")
    op.drop_index(op.f("ix_claims_org_id"), table_name="claims")
    op.drop_index(op.f("ix_claims_funding_source"), table_name="claims")
    op.drop_index(op.f("ix_claims_doctor_id"), table_name="claims")
    op.drop_index(op.f("ix_claims_date_start"), table_name="claims")
    op.drop_index(op.f("ix_claims_care_type"), table_name="claims")
    op.drop_table("claims")
    op.drop_index(op.f("ix_reg_chunks_doc_id"), table_name="reg_chunks")
    op.drop_table("reg_chunks")
    op.drop_table("quarantine_rows")
    op.drop_index(op.f("ix_doctors_org_id"), table_name="doctors")
    op.drop_table("doctors")
    op.drop_index(op.f("ix_contracts_org_id"), table_name="contracts")
    op.drop_table("contracts")
    op.drop_table("users")
    op.drop_table("rules")
    op.drop_table("rule_runs")
    op.drop_table("reg_documents")
    op.drop_table("patients")
    op.drop_index(op.f("ix_package_mapping_service_code"), table_name="package_mapping")
    op.drop_index(op.f("ix_package_mapping_icd10"), table_name="package_mapping")
    op.drop_table("package_mapping")
    op.drop_table("organizations")
    op.drop_table("import_files")
    op.drop_table("deadlines")
    op.drop_table("audit_log")
    op.drop_index(op.f("ix_alerts_status"), table_name="alerts")
    op.drop_table("alerts")
    # ### end Alembic commands ###
