"""add_email_to_organizations

Revision ID: add_email_org_2026
Revises: 0722de807eb5
Create Date: 2026-01-03 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_email_org_2026'
down_revision = '0722de807eb5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add email column to organizations table
    op.add_column('organizations', sa.Column('email', sa.String(length=255), nullable=True))


def downgrade() -> None:
    # Remove email column from organizations table
    op.drop_column('organizations', 'email')
