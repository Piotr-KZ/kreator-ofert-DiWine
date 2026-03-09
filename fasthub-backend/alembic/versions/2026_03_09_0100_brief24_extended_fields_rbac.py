"""Brief 24: Extended model fields + MemberRole enum expansion

Adds:
- User: phone, position, language, timezone
- Organization: legal_form, regon, krs, website, logo_url, rodo_inspector_name, rodo_inspector_email
- MemberRole enum: 'owner', 'editor' values
- Data migration: org owners get role='owner', rename RBAC role names

Revision ID: brief24_extended_fields_rbac
Revises: add_payment_gateway_columns
Create Date: 2026-03-09 01:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "brief24_extended_fields_rbac"
down_revision = "add_payment_gateway_columns"
branch_labels = None
depends_on = None


def upgrade():
    # === 1. Add new User columns ===
    op.add_column('users', sa.Column('phone', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('position', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('language', sa.String(10), nullable=True, server_default='pl'))
    op.add_column('users', sa.Column('timezone', sa.String(50), nullable=True, server_default='Europe/Warsaw'))

    # === 2. Add new Organization columns ===
    op.add_column('organizations', sa.Column('legal_form', sa.String(100), nullable=True))
    op.add_column('organizations', sa.Column('regon', sa.String(20), nullable=True))
    op.add_column('organizations', sa.Column('krs', sa.String(20), nullable=True))
    op.add_column('organizations', sa.Column('website', sa.String(500), nullable=True))
    op.add_column('organizations', sa.Column('logo_url', sa.String(500), nullable=True))
    op.add_column('organizations', sa.Column('rodo_inspector_name', sa.String(255), nullable=True))
    op.add_column('organizations', sa.Column('rodo_inspector_email', sa.String(255), nullable=True))

    # === 3. Drop redundant CHECK constraint (native PG enum enforces values) ===
    op.execute("ALTER TABLE members DROP CONSTRAINT IF EXISTS ck_member_role")

    # === 4. Expand MemberRole enum ===
    # PostgreSQL ALTER TYPE ADD VALUE cannot run inside a transaction
    op.execute("COMMIT")
    op.execute("ALTER TYPE memberrole ADD VALUE IF NOT EXISTS 'owner'")
    op.execute("ALTER TYPE memberrole ADD VALUE IF NOT EXISTS 'editor'")
    op.execute("BEGIN")

    # === 5. Data migration: set owner role for org owners ===
    op.execute("""
        UPDATE members m
        SET role = 'owner'
        FROM organizations o
        WHERE m.organization_id = o.id
          AND m.user_id = o.owner_id
          AND m.role = 'admin'
    """)

    # === 6. Rename RBAC system roles ===
    op.execute("""
        UPDATE roles SET name = 'Właściciel', description = 'Pełna kontrola nad organizacją'
        WHERE name = 'Owner' AND is_system = true
    """)
    op.execute("""
        UPDATE roles SET name = 'Podgląd', description = 'Tylko podgląd danych organizacji', is_default = false
        WHERE name = 'Member' AND is_system = true
    """)


def downgrade():
    # Remove Organization columns
    op.drop_column('organizations', 'rodo_inspector_email')
    op.drop_column('organizations', 'rodo_inspector_name')
    op.drop_column('organizations', 'logo_url')
    op.drop_column('organizations', 'website')
    op.drop_column('organizations', 'krs')
    op.drop_column('organizations', 'regon')
    op.drop_column('organizations', 'legal_form')

    # Remove User columns
    op.drop_column('users', 'timezone')
    op.drop_column('users', 'language')
    op.drop_column('users', 'position')
    op.drop_column('users', 'phone')

    # Revert RBAC role names
    op.execute("""
        UPDATE roles SET name = 'Owner', description = 'Właściciel organizacji — pełne uprawnienia'
        WHERE name = 'Właściciel' AND is_system = true
    """)
    op.execute("""
        UPDATE roles SET name = 'Member', description = 'Zwykły członek — podstawowe uprawnienia', is_default = true
        WHERE name = 'Podgląd' AND is_system = true
    """)

    # Revert owner members back to admin
    op.execute("UPDATE members SET role = 'admin' WHERE role = 'owner'")
    # Revert editor members back to viewer
    op.execute("UPDATE members SET role = 'viewer' WHERE role = 'editor'")

    # NOTE: PostgreSQL does not support ALTER TYPE DROP VALUE.
    # The enum values 'owner' and 'editor' will remain but unused.
