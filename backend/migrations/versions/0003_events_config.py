"""events feed + app_config key-value store (EPIC G2/G4).

Revision ID: 0003_events_config
Revises: 0002_auth_users
Create Date: 2026-07-09

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_events_config"
down_revision: str | None = "0002_auth_users"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("type", sa.String(length=48), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("actor", sa.String(length=128), nullable=False),
        sa.Column("actor_username", sa.String(length=64), nullable=True),
        sa.Column("role", sa.String(length=32), nullable=True),
        sa.Column("entity_ref", sa.String(length=160), nullable=True),
        sa.Column("link", sa.String(length=255), nullable=True),
        sa.Column("title_kk", sa.Text(), nullable=False),
        sa.Column("title_ru", sa.Text(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
    )
    op.create_index(op.f("ix_events_ts"), "events", ["ts"])
    op.create_index(op.f("ix_events_type"), "events", ["type"])
    op.create_table(
        "app_config",
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("value", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("key", name=op.f("pk_app_config")),
    )


def downgrade() -> None:
    op.drop_table("app_config")
    op.drop_index(op.f("ix_events_type"), table_name="events")
    op.drop_index(op.f("ix_events_ts"), table_name="events")
    op.drop_table("events")
