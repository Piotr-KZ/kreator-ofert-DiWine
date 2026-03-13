"""Brief 35: form_submissions table"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "brief35_form_sub"
down_revision = "brief30_webcreator"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "form_submissions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("site_id", UUID(as_uuid=True), sa.ForeignKey("published_sites.id"), nullable=False),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("data_json", JSONB, nullable=False),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("read", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_fs_site", "form_submissions", ["site_id"])
    op.create_index("ix_fs_org", "form_submissions", ["organization_id"])


def downgrade():
    op.drop_table("form_submissions")
