"""add_indexes_for_search

Revision ID: 0722de807eb5
Revises: add_members_table
Create Date: 2026-01-02 03:01:04.813961

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0722de807eb5'
down_revision = 'add_members_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add indexes for search performance on users table
    # Note: ix_users_email already exists (created by SQLAlchemy)
    op.create_index('ix_users_full_name', 'users', ['full_name'], unique=False)
    
    # Add composite index for search queries (email + full_name)
    op.create_index('ix_users_search', 'users', ['email', 'full_name'], unique=False)


def downgrade() -> None:
    # Remove indexes
    op.drop_index('ix_users_search', table_name='users')
    op.drop_index('ix_users_full_name', table_name='users')
