"""Add performance indexes

Revision ID: add_performance_indexes
Revises: 6abaa640d27e
Create Date: 2026-01-03 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_performance_indexes'
down_revision = '6abaa640d27e'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add indexes for performance optimization
    
    Indexes added:
    - users.magic_link_token: Fast lookup for magic link authentication
    - members.role: Filter members by role
    - organizations.owner_id: Find organizations by owner
    - audit_logs.user_id: User activity history queries
    """
    # Add index to users.magic_link_token
    op.create_index(
        'ix_users_magic_link_token',
        'users',
        ['magic_link_token'],
        unique=False
    )
    
    # Add index to members.role
    op.create_index(
        'ix_members_role',
        'members',
        ['role'],
        unique=False
    )
    
    # Add index to organizations.owner_id
    op.create_index(
        'ix_organizations_owner_id',
        'organizations',
        ['owner_id'],
        unique=False
    )
    
    # Add index to audit_logs.user_id
    op.create_index(
        'ix_audit_logs_user_id',
        'audit_logs',
        ['user_id'],
        unique=False
    )


def downgrade():
    """Remove performance indexes"""
    op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')
    op.drop_index('ix_organizations_owner_id', table_name='organizations')
    op.drop_index('ix_members_role', table_name='members')
    op.drop_index('ix_users_magic_link_token', table_name='users')
