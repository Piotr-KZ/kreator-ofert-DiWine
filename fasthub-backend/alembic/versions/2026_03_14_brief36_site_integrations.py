"""Brief 36: site_integrations table

Revision ID: brief36_site_int
Revises: brief35_form_sub
Create Date: 2026-03-14
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "brief36_site_int"
down_revision = "brief35_form_sub"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "site_integrations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "site_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("published_sites.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), server_default="configured"),
        sa.Column("config_json", postgresql.JSONB),
        sa.Column("connected_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("last_sync_at", sa.DateTime),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_si_site", "site_integrations", ["site_id"])


def downgrade() -> None:
    op.drop_index("ix_si_site")
    op.drop_table("site_integrations")
