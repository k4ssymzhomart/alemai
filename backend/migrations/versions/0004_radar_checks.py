"""radar_checks — normative-source version checks (EPIC G5).

Revision ID: 0004_radar_checks
Revises: 0003_events_config
Create Date: 2026-07-09

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_radar_checks"
down_revision: str | None = "0003_events_config"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "radar_checks",
        sa.Column("source_id", sa.String(length=48), nullable=False),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("our_version", sa.String(length=64), nullable=True),
        sa.Column("detected_version", sa.String(length=64), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("source_id", name=op.f("pk_radar_checks")),
    )


def downgrade() -> None:
    op.drop_table("radar_checks")
