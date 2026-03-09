"""Brief 26: 2FA TOTP fields + UserSession table

Adds:
- User: totp_secret, totp_enabled, totp_verified_at, backup_codes
- New table: user_sessions (session tracking per device)

Revision ID: brief26_2fa_sessions
Revises: brief24_extended_fields_rbac
Create Date: 2026-03-09 02:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = "brief26_2fa_sessions"
down_revision = "brief24_extended_fields_rbac"
branch_labels = None
depends_on = None


def upgrade():
    # === 1. Add TOTP fields to users ===
    op.add_column('users', sa.Column('totp_secret', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('totp_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('totp_verified_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('backup_codes', sa.Text(), nullable=True))

    # === 2. Create user_sessions table ===
    op.create_table(
        'user_sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('token_jti', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('device_type', sa.String(50), nullable=True),
        sa.Column('device_name', sa.String(255), nullable=True),
        sa.Column('browser', sa.String(100), nullable=True),
        sa.Column('os', sa.String(100), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_active_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('user_sessions')
    op.drop_column('users', 'backup_codes')
    op.drop_column('users', 'totp_verified_at')
    op.drop_column('users', 'totp_enabled')
    op.drop_column('users', 'totp_secret')
