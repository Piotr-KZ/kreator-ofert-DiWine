"""Add members table for multi-org support

Revision ID: add_members_table
Revises: add_org_billing
Create Date: 2026-01-01 20:00:00.000000

CRITICAL MIGRATION:
1. Creates members table (many-to-many: users ←→ organizations)
2. Migrates existing user.organization_id → members
3. Drops user.organization_id column (BREAKING CHANGE!)
4. Keeps organization.owner_id (owner ≠ member concept)
5. Adds is_superuser to users for SuperAdmin support

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM, UUID


# revision identifiers, used by Alembic.
revision = 'add_members_table'
down_revision = 'add_org_billing'
branch_labels = None
depends_on = None


def upgrade():
    print("\n" + "="*80)
    print("CRITICAL MIGRATION: Adding Members Table")
    print("="*80)
    
    # 1. Add is_superuser to users table (for SuperAdmin support)
    print("Step 1/8: Adding is_superuser column to users...")
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'is_superuser' not in columns:
        op.add_column('users',
            sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false')
        )
        print("  ✓ Added is_superuser column")
    else:
        print("  ✓ is_superuser column already exists")
    
    # 2. Create members table (using String for role with CHECK constraint)
    print("Step 3/8: Creating members table...")
    op.create_table(
        'members',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, server_default='admin'),
        sa.Column('joined_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        
        # Unique constraint: user can be member of org only once
        sa.UniqueConstraint('user_id', 'organization_id', name='uq_user_organization'),
        # Check constraint for role values
        sa.CheckConstraint("role IN ('admin', 'viewer')", name='ck_member_role')
    )
    
    # 4. Create indexes for performance
    print("Step 4/8: Creating indexes...")
    op.create_index('idx_members_user', 'members', ['user_id'])
    op.create_index('idx_members_org', 'members', ['organization_id'])
    
    # 5. Migrate existing data: users.organization_id → members
    print("Step 5/8: Migrating existing users to members...")
    op.execute("""
        INSERT INTO members (user_id, organization_id, role, joined_at, created_at, updated_at)
        SELECT 
            u.id as user_id,
            u.organization_id,
            'admin' as role,
            u.created_at as joined_at,
            u.created_at,
            u.updated_at
        FROM users u
        WHERE u.organization_id IS NOT NULL
    """)
    
    # 6. Ensure all organization owners have membership
    print("Step 6/8: Adding owner memberships...")
    op.execute("""
        INSERT INTO members (user_id, organization_id, role, joined_at, created_at, updated_at)
        SELECT 
            o.owner_id as user_id,
            o.id as organization_id,
            'admin' as role,
            o.created_at as joined_at,
            o.created_at,
            o.updated_at
        FROM organizations o
        WHERE o.owner_id IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM members m 
            WHERE m.user_id = o.owner_id 
            AND m.organization_id = o.id
        )
    """)
    
    # 7. Drop users.organization_id (BREAKING CHANGE!)
    print("Step 7/8: Dropping users.organization_id column...")
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'organization_id' in columns:
        # Drop FK constraint if exists (using raw SQL to avoid transaction abort)
        op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_organization_id_fkey")
        op.drop_column('users', 'organization_id')
        print("  ✓ Dropped organization_id column")
    else:
        print("  ✓ organization_id column already removed")
    
    # 8. Drop UserRole enum from users.role (will use MemberRole in members table)
    print("Step 8/8: Cleaning up old role column...")
    if 'role' in columns:
        op.drop_column('users', 'role')
        print("  ✓ Dropped role column")
        # Try to drop UserRole enum if it exists
        try:
            op.execute("DROP TYPE IF EXISTS userrole")
            print("  ✓ Dropped userrole enum")
        except Exception as e:
            print(f"  Warning: Could not drop userrole enum: {e}")
    else:
        print("  ✓ role column already removed")
    
    print("\n" + "="*80)
    print("MIGRATION COMPLETE!")
    print("="*80)
    print("IMPORTANT: Manual steps required:")
    print("1. Set SuperAdmin: UPDATE users SET is_superuser = true WHERE email = 'your@email.com';")
    print("2. Verify members: SELECT * FROM members;")
    print("3. Test multi-org: Users can now belong to multiple organizations!")
    print("="*80 + "\n")


def downgrade():
    print("\n" + "="*80)
    print("WARNING: DESTRUCTIVE DOWNGRADE!")
    print("Multi-org memberships will be LOST!")
    print("="*80)
    
    # Add back users.role column
    from sqlalchemy import Enum as SQLEnum
    import enum
    
    class UserRole(str, enum.Enum):
        admin = "admin"
        user = "user"
        viewer = "viewer"
    
    op.add_column('users',
        sa.Column('role', SQLEnum(UserRole), nullable=False, server_default='user')
    )
    
    # Add back organization_id column
    op.add_column('users',
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=True)
    )
    
    # Try to restore first membership (arbitrary choice if user has multiple!)
    op.execute("""
        UPDATE users u
        SET organization_id = (
            SELECT m.organization_id 
            FROM members m 
            WHERE m.user_id = u.id 
            ORDER BY m.joined_at ASC 
            LIMIT 1
        )
        WHERE EXISTS (
            SELECT 1 FROM members m WHERE m.user_id = u.id
        )
    """)
    
    # Drop members table
    op.drop_index('idx_members_org', 'members')
    op.drop_index('idx_members_user', 'members')
    op.drop_table('members')
    
    # Drop MemberRole enum
    op.execute("DROP TYPE IF EXISTS memberrole")
    
    # Drop is_superuser
    op.drop_column('users', 'is_superuser')
    
    print("Downgrade complete. Data loss may have occurred.")
