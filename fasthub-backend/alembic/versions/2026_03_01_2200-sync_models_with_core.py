"""Sync database schema with fasthub_core models

Adds missing tables and columns from phases 1.1-1.6:
- users: is_superadmin, is_email_verified, email_verified_at
- audit_logs: user_email, impersonated_by, organization_id, changes_before, changes_after, summary, resource_id type fix
- New tables: permissions, roles, role_permissions, user_roles, notifications, notification_preferences

Revision ID: sync_models_with_core
Revises: convert_member_role_to_enum
Create Date: 2026-03-01 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'sync_models_with_core'
down_revision = 'convert_member_role_to_enum'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # ── 1. Add missing columns to users ──
    user_columns = [col['name'] for col in inspector.get_columns('users')]

    if 'is_superadmin' not in user_columns:
        op.add_column('users',
            sa.Column('is_superadmin', sa.Boolean(), nullable=False, server_default='false')
        )

    if 'is_email_verified' not in user_columns:
        op.add_column('users',
            sa.Column('is_email_verified', sa.Boolean(), nullable=False, server_default='false')
        )

    if 'email_verified_at' not in user_columns:
        op.add_column('users',
            sa.Column('email_verified_at', sa.DateTime(), nullable=True)
        )

    # ── 2. Add missing columns to audit_logs ──
    audit_columns = [col['name'] for col in inspector.get_columns('audit_logs')]

    if 'user_email' not in audit_columns:
        op.add_column('audit_logs',
            sa.Column('user_email', sa.String(255), nullable=True)
        )

    if 'impersonated_by' not in audit_columns:
        op.add_column('audit_logs',
            sa.Column('impersonated_by', UUID(as_uuid=True), nullable=True)
        )

    if 'organization_id' not in audit_columns:
        op.add_column('audit_logs',
            sa.Column('organization_id', UUID(as_uuid=True),
                       sa.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True)
        )

    if 'changes_before' not in audit_columns:
        op.add_column('audit_logs',
            sa.Column('changes_before', sa.JSON(), nullable=True)
        )

    if 'changes_after' not in audit_columns:
        op.add_column('audit_logs',
            sa.Column('changes_after', sa.JSON(), nullable=True)
        )

    if 'summary' not in audit_columns:
        op.add_column('audit_logs',
            sa.Column('summary', sa.Text(), nullable=True)
        )

    # Rename details -> metadata (column name in DB; Python attr is extra_data)
    if 'details' in audit_columns and 'metadata' not in audit_columns:
        op.alter_column('audit_logs', 'details', new_column_name='metadata')

    # Fix resource_id type: UUID -> String(255) to match model
    # (model uses String(255) for resource_id)
    if 'resource_id' in audit_columns:
        op.alter_column('audit_logs', 'resource_id',
                         type_=sa.String(255),
                         existing_type=UUID(as_uuid=True),
                         existing_nullable=True,
                         postgresql_using='resource_id::text')

    # Add composite indexes for audit_logs
    op.create_index('ix_audit_org_created', 'audit_logs', ['organization_id', 'created_at'],
                     if_not_exists=True)
    op.create_index('ix_audit_user_created', 'audit_logs', ['user_id', 'created_at'],
                     if_not_exists=True)
    op.create_index('ix_audit_resource', 'audit_logs', ['resource_type', 'resource_id'],
                     if_not_exists=True)

    # ── 3. Create permissions table ──
    if 'permissions' not in existing_tables:
        op.create_table(
            'permissions',
            sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('category', sa.String(50), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('is_system', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index('ix_permissions_name', 'permissions', ['name'], unique=True)
        op.create_index('ix_permissions_category', 'permissions', ['category'])

    # ── 4. Create roles table ──
    if 'roles' not in existing_tables:
        op.create_table(
            'roles',
            sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('organization_id', UUID(as_uuid=True),
                       sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('is_system', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )

    # ── 5. Create role_permissions table ──
    if 'role_permissions' not in existing_tables:
        op.create_table(
            'role_permissions',
            sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('role_id', UUID(as_uuid=True),
                       sa.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False),
            sa.Column('permission_id', UUID(as_uuid=True),
                       sa.ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False),
        )

    # ── 6. Create user_roles table ──
    if 'user_roles' not in existing_tables:
        op.create_table(
            'user_roles',
            sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('user_id', UUID(as_uuid=True),
                       sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('role_id', UUID(as_uuid=True),
                       sa.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False),
            sa.Column('organization_id', UUID(as_uuid=True),
                       sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
            sa.Column('assigned_at', sa.DateTime(), nullable=True),
            sa.Column('assigned_by', UUID(as_uuid=True),
                       sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        )

    # ── 7. Create notifications table ──
    if 'notifications' not in existing_tables:
        op.create_table(
            'notifications',
            sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('user_id', UUID(as_uuid=True),
                       sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('organization_id', UUID(as_uuid=True),
                       sa.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True),
            sa.Column('type', sa.String(50), nullable=False),
            sa.Column('title', sa.String(255), nullable=False),
            sa.Column('message', sa.Text(), nullable=True),
            sa.Column('link', sa.String(500), nullable=True),
            sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('read_at', sa.DateTime(), nullable=True),
            sa.Column('triggered_by', UUID(as_uuid=True),
                       sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        )
        op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
        op.create_index('ix_notifications_type', 'notifications', ['type'])
        op.create_index('ix_notif_user_unread', 'notifications', ['user_id', 'is_read'])
        op.create_index('ix_notif_user_created', 'notifications', ['user_id', 'created_at'])

    # ── 8. Create notification_preferences table ──
    if 'notification_preferences' not in existing_tables:
        op.create_table(
            'notification_preferences',
            sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('user_id', UUID(as_uuid=True),
                       sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('notification_type', sa.String(50), nullable=False),
            sa.Column('channel_inapp', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('channel_email', sa.Boolean(), nullable=False, server_default='true'),
        )
        op.create_index('ix_notifpref_user_type', 'notification_preferences',
                         ['user_id', 'notification_type'], unique=True)


def downgrade():
    # Drop new tables (reverse order of creation)
    op.drop_table('notification_preferences')
    op.drop_table('notifications')
    op.drop_table('user_roles')
    op.drop_table('role_permissions')
    op.drop_table('roles')
    op.drop_table('permissions')

    # Revert audit_logs changes
    op.alter_column('audit_logs', 'resource_id',
                     type_=UUID(as_uuid=True),
                     existing_type=sa.String(255),
                     existing_nullable=True,
                     postgresql_using='resource_id::uuid')
    op.alter_column('audit_logs', 'metadata', new_column_name='details')
    op.drop_column('audit_logs', 'summary')
    op.drop_column('audit_logs', 'changes_after')
    op.drop_column('audit_logs', 'changes_before')
    op.drop_column('audit_logs', 'organization_id')
    op.drop_column('audit_logs', 'impersonated_by')
    op.drop_column('audit_logs', 'user_email')

    # Revert users changes
    op.drop_column('users', 'email_verified_at')
    op.drop_column('users', 'is_email_verified')
    op.drop_column('users', 'is_superadmin')
