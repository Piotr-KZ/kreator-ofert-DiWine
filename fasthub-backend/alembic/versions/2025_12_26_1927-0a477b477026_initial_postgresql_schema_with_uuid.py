"""Initial PostgreSQL schema with UUID

Revision ID: 0a477b477026
Revises: 
Create Date: 2025-12-26 19:27:29.061899

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a477b477026'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tables without foreign keys first
    op.create_table('organizations',
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('slug', sa.String(length=255), nullable=False),
    sa.Column('owner_id', sa.UUID(), nullable=True),
    sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('stripe_customer_id')
    )
    op.create_index(op.f('ix_organizations_created_at'), 'organizations', ['created_at'], unique=False)
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_slug'), 'organizations', ['slug'], unique=True)
    
    op.create_table('users',
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('magic_link_token', sa.String(length=255), nullable=True),
    sa.Column('magic_link_expires', sa.DateTime(), nullable=True),
    sa.Column('role', sa.Enum('admin', 'user', 'viewer', name='userrole'), nullable=False),
    sa.Column('organization_id', sa.UUID(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_created_at'), 'users', ['created_at'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    
    # Now add foreign keys
    op.create_foreign_key('fk_organizations_owner_id', 'organizations', 'users', ['owner_id'], ['id'])
    op.create_foreign_key('fk_users_organization_id', 'users', 'organizations', ['organization_id'], ['id'])
    
    # Create dependent tables
    op.create_table('api_tokens',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('token_hash', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('last_used_at', sa.DateTime(), nullable=True),
    sa.Column('expires_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_tokens_created_at'), 'api_tokens', ['created_at'], unique=False)
    op.create_index(op.f('ix_api_tokens_id'), 'api_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_api_tokens_token_hash'), 'api_tokens', ['token_hash'], unique=True)
    op.create_index(op.f('ix_api_tokens_user_id'), 'api_tokens', ['user_id'], unique=False)
    
    op.create_table('invoices',
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('invoice_number', sa.String(length=255), nullable=False),
    sa.Column('stripe_invoice_id', sa.String(length=255), nullable=True),
    sa.Column('fakturownia_id', sa.String(length=255), nullable=True),
    sa.Column('status', sa.Enum('DRAFT', 'OPEN', 'PAID', 'VOID', 'UNCOLLECTIBLE', name='invoicestatus'), nullable=False),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('pdf_url', sa.Text(), nullable=True),
    sa.Column('due_date', sa.DateTime(), nullable=True),
    sa.Column('paid_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('fakturownia_id'),
    sa.UniqueConstraint('invoice_number'),
    sa.UniqueConstraint('stripe_invoice_id')
    )
    op.create_index(op.f('ix_invoices_created_at'), 'invoices', ['created_at'], unique=False)
    op.create_index(op.f('ix_invoices_id'), 'invoices', ['id'], unique=False)
    
    op.create_table('subscriptions',
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('stripe_subscription_id', sa.String(length=255), nullable=False),
    sa.Column('stripe_price_id', sa.String(length=255), nullable=False),
    sa.Column('status', sa.Enum('active', 'canceled', 'incomplete', 'incomplete_expired', 'past_due', 'trialing', 'unpaid', name='subscriptionstatus'), nullable=False),
    sa.Column('current_period_start', sa.DateTime(), nullable=False),
    sa.Column('current_period_end', sa.DateTime(), nullable=False),
    sa.Column('cancel_at_period_end', sa.Boolean(), nullable=False),
    sa.Column('canceled_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('stripe_subscription_id')
    )
    op.create_index(op.f('ix_subscriptions_created_at'), 'subscriptions', ['created_at'], unique=False)
    op.create_index(op.f('ix_subscriptions_id'), 'subscriptions', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_subscriptions_id'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_created_at'), table_name='subscriptions')
    op.drop_table('subscriptions')
    op.drop_index(op.f('ix_invoices_id'), table_name='invoices')
    op.drop_index(op.f('ix_invoices_created_at'), table_name='invoices')
    op.drop_table('invoices')
    op.drop_index(op.f('ix_api_tokens_user_id'), table_name='api_tokens')
    op.drop_index(op.f('ix_api_tokens_token_hash'), table_name='api_tokens')
    op.drop_index(op.f('ix_api_tokens_id'), table_name='api_tokens')
    op.drop_index(op.f('ix_api_tokens_created_at'), table_name='api_tokens')
    op.drop_table('api_tokens')
    
    # Drop foreign keys before dropping tables
    op.drop_constraint('fk_users_organization_id', 'users', type_='foreignkey')
    op.drop_constraint('fk_organizations_owner_id', 'organizations', type_='foreignkey')
    
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_created_at'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_organizations_slug'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_id'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_created_at'), table_name='organizations')
    op.drop_table('organizations')
