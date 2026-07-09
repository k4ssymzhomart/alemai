"""share_links (H3) + document_versions + comments (H4).

Revision ID: 0005_share_docs
Revises: 0004_radar_checks
Create Date: 2026-07-09

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_share_docs"
down_revision: str | None = "0004_radar_checks"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "share_links",
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.Column("url_state", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_by", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("code", name=op.f("pk_share_links")),
    )
    op.create_table(
        "document_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("doc_type", sa.String(length=32), nullable=False),
        sa.Column("entity_ref", sa.String(length=160), nullable=True),
        sa.Column("params", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("author", sa.String(length=64), nullable=True),
        sa.Column("author_name", sa.String(length=128), nullable=True),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("auto_title", sa.Text(), nullable=False),
        sa.Column("lang", sa.String(length=4), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_versions")),
    )
    op.create_index(op.f("ix_document_versions_doc_type"), "document_versions", ["doc_type"])
    op.create_index(op.f("ix_document_versions_entity_ref"), "document_versions", ["entity_ref"])
    op.create_index(op.f("ix_document_versions_ts"), "document_versions", ["ts"])
    op.create_table(
        "comments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("entity_ref", sa.String(length=160), nullable=False),
        sa.Column("author", sa.String(length=64), nullable=True),
        sa.Column("author_name", sa.String(length=128), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("type", sa.String(length=24), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=True),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_comments")),
    )
    op.create_index(op.f("ix_comments_entity_ref"), "comments", ["entity_ref"])
    op.create_index(op.f("ix_comments_ts"), "comments", ["ts"])


def downgrade() -> None:
    op.drop_table("comments")
    op.drop_table("document_versions")
    op.drop_table("share_links")
