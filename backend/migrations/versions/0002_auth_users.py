"""auth — login identity + password hash + notifications cursor on users (G1).

Revision ID: 0002_auth_users
Revises: 0001
Create Date: 2026-07-09

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_auth_users"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(length=64), nullable=True))
    op.add_column("users", sa.Column("password_hash", sa.String(length=255), nullable=True))
    op.add_column(
        "users",
        sa.Column("notifications_read_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_unique_constraint(op.f("uq_users_username"), "users", ["username"])


def downgrade() -> None:
    op.drop_constraint(op.f("uq_users_username"), "users", type_="unique")
    op.drop_column("users", "notifications_read_at")
    op.drop_column("users", "password_hash")
    op.drop_column("users", "username")
