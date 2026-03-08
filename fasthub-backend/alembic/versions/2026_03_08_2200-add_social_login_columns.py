"""Add social login columns to users table (Brief 18)

Adds google_id, github_id, microsoft_id, oauth_provider, avatar_url
columns for Social Login support.

Revision ID: add_social_login_columns
Revises: billing_system_v2
Create Date: 2026-03-08 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_social_login_columns"
down_revision = "billing_system_v2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("google_id", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("github_id", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("microsoft_id", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("oauth_provider", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("avatar_url", sa.String(500), nullable=True))

    op.create_index("ix_users_google_id", "users", ["google_id"], unique=True)
    op.create_index("ix_users_github_id", "users", ["github_id"], unique=True)
    op.create_index("ix_users_microsoft_id", "users", ["microsoft_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_microsoft_id", table_name="users")
    op.drop_index("ix_users_github_id", table_name="users")
    op.drop_index("ix_users_google_id", table_name="users")

    op.drop_column("users", "avatar_url")
    op.drop_column("users", "oauth_provider")
    op.drop_column("users", "microsoft_id")
    op.drop_column("users", "github_id")
    op.drop_column("users", "google_id")
