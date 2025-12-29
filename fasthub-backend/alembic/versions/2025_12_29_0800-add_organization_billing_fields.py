"""Add billing fields and onboarding status to organizations

Revision ID: add_org_billing
Revises: 0a477b477026
Create Date: 2025-12-29 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_org_billing'
down_revision = '0a477b477026'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to organizations table
    op.add_column('organizations', sa.Column('type', sa.String(length=50), nullable=True))
    op.add_column('organizations', sa.Column('nip', sa.String(length=50), nullable=True))
    op.add_column('organizations', sa.Column('phone', sa.String(length=50), nullable=True))
    op.add_column('organizations', sa.Column('billing_street', sa.String(length=255), nullable=True))
    op.add_column('organizations', sa.Column('billing_city', sa.String(length=100), nullable=True))
    op.add_column('organizations', sa.Column('billing_postal_code', sa.String(length=20), nullable=True))
    op.add_column('organizations', sa.Column('billing_country', sa.String(length=100), nullable=True))
    op.add_column('organizations', sa.Column('is_complete', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Remove columns
    op.drop_column('organizations', 'is_complete')
    op.drop_column('organizations', 'billing_country')
    op.drop_column('organizations', 'billing_postal_code')
    op.drop_column('organizations', 'billing_city')
    op.drop_column('organizations', 'billing_street')
    op.drop_column('organizations', 'phone')
    op.drop_column('organizations', 'nip')
    op.drop_column('organizations', 'type')
