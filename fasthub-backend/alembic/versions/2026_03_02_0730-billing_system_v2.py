"""Billing System v2 — new models + Subscription extensions

Add: billing_plans, billing_addons, tenant_addons, usage_records, billing_events
Extend: subscriptions (plan_id, billing_interval, trial_end, stripe_customer_id)

Revision ID: billing_system_v2
Revises: add_basemodel_columns
Create Date: 2026-03-02 07:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'billing_system_v2'
down_revision = 'add_basemodel_columns'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # === NEW TABLES ===

    if 'billing_plans' not in existing_tables:
        op.create_table('billing_plans',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('slug', sa.String(50), unique=True, index=True, nullable=False),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('billing_mode', sa.String(20), server_default='fixed'),
            sa.Column('price_monthly', sa.Float(), server_default='0.0'),
            sa.Column('price_yearly', sa.Float(), server_default='0.0'),
            sa.Column('currency', sa.String(3), server_default='PLN'),
            sa.Column('stripe_price_monthly_id', sa.String(100), nullable=True),
            sa.Column('stripe_price_yearly_id', sa.String(100), nullable=True),
            sa.Column('stripe_product_id', sa.String(100), nullable=True),
            sa.Column('max_processes', sa.Integer(), server_default='3'),
            sa.Column('max_executions_month', sa.Integer(), server_default='100'),
            sa.Column('max_integrations', sa.Integer(), server_default='3'),
            sa.Column('max_ai_operations_month', sa.Integer(), server_default='50'),
            sa.Column('max_team_members', sa.Integer(), server_default='1'),
            sa.Column('max_file_storage_mb', sa.Integer(), server_default='100'),
            sa.Column('features', sa.JSON(), nullable=True),
            sa.Column('sort_order', sa.Integer(), server_default='0'),
            sa.Column('badge', sa.String(50), nullable=True),
            sa.Column('color', sa.String(7), nullable=True),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('is_default', sa.Boolean(), server_default='false'),
            sa.Column('is_visible', sa.Boolean(), server_default='true'),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        )

    if 'billing_addons' not in existing_tables:
        op.create_table('billing_addons',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('slug', sa.String(50), unique=True, index=True, nullable=False),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('resource_type', sa.String(50), nullable=False),
            sa.Column('quantity', sa.Integer(), server_default='0'),
            sa.Column('price_monthly', sa.Float(), server_default='0.0'),
            sa.Column('price_yearly', sa.Float(), server_default='0.0'),
            sa.Column('currency', sa.String(3), server_default='PLN'),
            sa.Column('stripe_price_monthly_id', sa.String(100), nullable=True),
            sa.Column('stripe_price_yearly_id', sa.String(100), nullable=True),
            sa.Column('stripe_product_id', sa.String(100), nullable=True),
            sa.Column('available_for_plans', sa.JSON(), nullable=True),
            sa.Column('max_quantity_per_tenant', sa.Integer(), server_default='0'),
            sa.Column('sort_order', sa.Integer(), server_default='0'),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        )

    if 'tenant_addons' not in existing_tables:
        op.create_table('tenant_addons',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('tenant_id', sa.String(100), index=True, nullable=False),
            sa.Column('addon_id', sa.Integer(), sa.ForeignKey('billing_addons.id'), nullable=False),
            sa.Column('quantity', sa.Integer(), server_default='1'),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('stripe_subscription_item_id', sa.String(100), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
            sa.Column('expires_at', sa.DateTime(), nullable=True),
        )

    if 'usage_records' not in existing_tables:
        op.create_table('usage_records',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('tenant_id', sa.String(100), index=True, nullable=False),
            sa.Column('period', sa.String(7), index=True, nullable=False),
            sa.Column('executions_count', sa.Integer(), server_default='0'),
            sa.Column('ai_operations_count', sa.Integer(), server_default='0'),
            sa.Column('active_processes_count', sa.Integer(), server_default='0'),
            sa.Column('active_integrations_count', sa.Integer(), server_default='0'),
            sa.Column('storage_used_mb', sa.Float(), server_default='0.0'),
            sa.Column('webhook_calls_count', sa.Integer(), server_default='0'),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        )

    if 'billing_events' not in existing_tables:
        op.create_table('billing_events',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('tenant_id', sa.String(100), index=True, nullable=False),
            sa.Column('event_type', sa.String(100), index=True, nullable=False),
            sa.Column('stripe_event_id', sa.String(100), nullable=True, unique=True),
            sa.Column('data', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        )

    # === EXTEND SUBSCRIPTIONS ===

    sub_cols = [col['name'] for col in inspector.get_columns('subscriptions')]

    if 'plan_id' not in sub_cols:
        op.add_column('subscriptions',
            sa.Column('plan_id', sa.Integer(), sa.ForeignKey('billing_plans.id'), nullable=True)
        )

    if 'billing_interval' not in sub_cols:
        op.add_column('subscriptions',
            sa.Column('billing_interval', sa.String(20), nullable=True)
        )

    if 'trial_end' not in sub_cols:
        op.add_column('subscriptions',
            sa.Column('trial_end', sa.DateTime(), nullable=True)
        )

    if 'stripe_customer_id' not in sub_cols:
        op.add_column('subscriptions',
            sa.Column('stripe_customer_id', sa.String(255), nullable=True)
        )


def downgrade():
    # Drop new columns from subscriptions
    op.drop_column('subscriptions', 'stripe_customer_id')
    op.drop_column('subscriptions', 'trial_end')
    op.drop_column('subscriptions', 'billing_interval')
    op.drop_column('subscriptions', 'plan_id')

    # Drop new tables
    op.drop_table('billing_events')
    op.drop_table('usage_records')
    op.drop_table('tenant_addons')
    op.drop_table('billing_addons')
    op.drop_table('billing_plans')
