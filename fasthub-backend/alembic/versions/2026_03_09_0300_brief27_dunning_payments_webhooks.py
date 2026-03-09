"""Brief 27: Dunning paths + payments + webhook config tables

Adds:
- dunning_paths: konfigurowalna sciezka windykacyjna
- dunning_steps: kroki w sciezce
- dunning_events: log wykonanych akcji
- payments: historia platnosci dla klienta
- webhook_endpoints: konfiguracja webhookow per organizacja
- webhook_deliveries: log wyslanych webhookow

Revision ID: brief27_dunning_pay_wh
Revises: brief26_2fa_sessions
Create Date: 2026-03-09 03:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = "brief27_dunning_pay_wh"
down_revision = "brief26_2fa_sessions"
branch_labels = None
depends_on = None


def upgrade():
    # === 1. dunning_paths ===
    op.create_table(
        'dunning_paths',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_default', sa.Boolean(), default=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('applicable_plans', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # === 2. dunning_steps ===
    dunning_action_type = sa.Enum(
        'email_reminder', 'email_warning', 'email_final',
        'retry_payment', 'restrict_access', 'block_access',
        'downgrade_free', 'cancel_subscription', 'disable_sites',
        'notify_admin', 'webhook',
        name='dunningactiontype',
    )

    op.create_table(
        'dunning_steps',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('path_id', UUID(as_uuid=True), sa.ForeignKey('dunning_paths.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('day_offset', sa.Integer(), nullable=False),
        sa.Column('action_type', dunning_action_type, nullable=False),
        sa.Column('email_template_id', sa.String(100), nullable=True),
        sa.Column('email_subject', sa.String(500), nullable=True),
        sa.Column('email_body_override', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # === 3. dunning_events ===
    op.create_table(
        'dunning_events',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('subscription_id', UUID(as_uuid=True), sa.ForeignKey('subscriptions.id'), nullable=False, index=True),
        sa.Column('organization_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('step_id', UUID(as_uuid=True), sa.ForeignKey('dunning_steps.id'), nullable=True),
        sa.Column('day_offset', sa.Integer(), nullable=False),
        sa.Column('action_type', dunning_action_type, nullable=False),
        sa.Column('status', sa.String(50), default='executed'),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('executed_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # === 4. payments ===
    op.create_table(
        'payments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False, index=True),
        sa.Column('subscription_id', UUID(as_uuid=True), sa.ForeignKey('subscriptions.id'), nullable=True),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='PLN'),
        sa.Column('gateway_id', sa.String(50), nullable=False),
        sa.Column('gateway_payment_id', sa.String(255), nullable=True),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('payment_method_details', sa.String(255), nullable=True),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('failed_at', sa.DateTime(), nullable=True),
        sa.Column('refunded_at', sa.DateTime(), nullable=True),
        sa.Column('invoice_id', UUID(as_uuid=True), sa.ForeignKey('invoices.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # === 5. webhook_endpoints ===
    op.create_table(
        'webhook_endpoints',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('url', sa.String(1000), nullable=False),
        sa.Column('secret', sa.String(255), nullable=False),
        sa.Column('events', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_triggered_at', sa.DateTime(), nullable=True),
        sa.Column('last_status_code', sa.Integer(), nullable=True),
        sa.Column('consecutive_failures', sa.Integer(), default=0),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # === 6. webhook_deliveries ===
    op.create_table(
        'webhook_deliveries',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('endpoint_id', UUID(as_uuid=True), sa.ForeignKey('webhook_endpoints.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('success', sa.Boolean(), default=False),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('attempt', sa.Integer(), default=1),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('webhook_deliveries')
    op.drop_table('webhook_endpoints')
    op.drop_table('payments')
    op.drop_table('dunning_events')
    op.drop_table('dunning_steps')
    op.drop_table('dunning_paths')
    sa.Enum(name='dunningactiontype').drop(op.get_bind(), checkfirst=True)
