"""create_audit_logs_table

Revision ID: 6abaa640d27e
Revises: 0722de807eb5
Create Date: 2026-01-02 03:04:04.694736

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid


# revision identifiers, used by Alembic.
revision = '6abaa640d27e'
down_revision = '0722de807eb5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),  # e.g., 'user.delete', 'user.update'
        sa.Column('resource_type', sa.String(50), nullable=False),  # e.g., 'user', 'organization'
        sa.Column('resource_id', UUID(as_uuid=True), nullable=True),
        sa.Column('details', sa.JSON, nullable=True),  # Additional context (what changed, etc.)
        sa.Column('ip_address', sa.String(45), nullable=True),  # IPv4 or IPv6
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    
    # Add indexes for common queries
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_resource_type', 'audit_logs', ['resource_type'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])


def downgrade() -> None:
    # Remove indexes
    op.drop_index('ix_audit_logs_created_at', table_name='audit_logs')
    op.drop_index('ix_audit_logs_resource_type', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action', table_name='audit_logs')
    op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')
    
    # Drop table
    op.drop_table('audit_logs')
