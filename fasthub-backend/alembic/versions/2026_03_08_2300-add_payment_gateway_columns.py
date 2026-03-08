"""Add payment gateway columns to subscriptions table (Brief 20)

Adds gateway_id, amount, currency, gateway_customer_id, gateway_payment_token,
last_renewal_attempt, renewal_failures, grace_period_end columns for
multi-gateway support (PayU, tPay, P24, PayPal).

Revision ID: add_payment_gateway_columns
Revises: add_social_login_columns
Create Date: 2026-03-08 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_payment_gateway_columns"
down_revision = "add_social_login_columns"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    sub_cols = [col["name"] for col in inspector.get_columns("subscriptions")]

    if "gateway_id" not in sub_cols:
        op.add_column("subscriptions", sa.Column("gateway_id", sa.String(50), nullable=True))
    if "amount" not in sub_cols:
        op.add_column("subscriptions", sa.Column("amount", sa.Integer(), nullable=True))
    if "currency" not in sub_cols:
        op.add_column("subscriptions", sa.Column("currency", sa.String(3), server_default="PLN"))
    if "gateway_customer_id" not in sub_cols:
        op.add_column("subscriptions", sa.Column("gateway_customer_id", sa.String(200), nullable=True))
    if "gateway_payment_token" not in sub_cols:
        op.add_column("subscriptions", sa.Column("gateway_payment_token", sa.String(200), nullable=True))
    if "last_renewal_attempt" not in sub_cols:
        op.add_column("subscriptions", sa.Column("last_renewal_attempt", sa.DateTime(), nullable=True))
    if "renewal_failures" not in sub_cols:
        op.add_column("subscriptions", sa.Column("renewal_failures", sa.Integer(), server_default="0"))
    if "grace_period_end" not in sub_cols:
        op.add_column("subscriptions", sa.Column("grace_period_end", sa.DateTime(), nullable=True))
    if "cancel_at_period_end" not in sub_cols:
        op.add_column("subscriptions", sa.Column("cancel_at_period_end", sa.Boolean(), server_default="false"))
    if "canceled_at" not in sub_cols:
        op.add_column("subscriptions", sa.Column("canceled_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("subscriptions", "canceled_at")
    op.drop_column("subscriptions", "cancel_at_period_end")
    op.drop_column("subscriptions", "grace_period_end")
    op.drop_column("subscriptions", "renewal_failures")
    op.drop_column("subscriptions", "last_renewal_attempt")
    op.drop_column("subscriptions", "gateway_payment_token")
    op.drop_column("subscriptions", "gateway_customer_id")
    op.drop_column("subscriptions", "currency")
    op.drop_column("subscriptions", "amount")
    op.drop_column("subscriptions", "gateway_id")
