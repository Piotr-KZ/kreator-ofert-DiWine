"""Brief 41: AI Visibility — ai_visibility on projects, llms_txt + openapi_json on published_sites

Revision ID: brief41_ai_vis
Revises: brief36_site_int
Create Date: 2026-04-18
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "brief41_ai_vis"
down_revision = "brief36_site_int"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("projects", sa.Column("ai_visibility", postgresql.JSONB(), server_default="{}"))
    op.add_column("published_sites", sa.Column("llms_txt", sa.Text(), nullable=True))
    op.add_column("published_sites", sa.Column("openapi_json", postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column("published_sites", "openapi_json")
    op.drop_column("published_sites", "llms_txt")
    op.drop_column("projects", "ai_visibility")
