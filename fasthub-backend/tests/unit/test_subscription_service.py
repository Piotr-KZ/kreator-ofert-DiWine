import pytest
from app.services.subscription_service import SubscriptionService
from app.models.subscription import Subscription, SubscriptionStatus

@pytest.fixture
def subscription_service():
    return SubscriptionService()

@pytest.mark.asyncio
async def test_create_subscription(db_session, subscription_service, test_organization):
    """Test subscription creation"""
    sub = await subscription_service.create(
        db_session,
        organization_id=test_organization.id,
        plan_id="pro",
        stripe_subscription_id="sub_123"
    )
    assert sub.status == SubscriptionStatus.ACTIVE
    assert sub.plan_id == "pro"

@pytest.mark.asyncio
async def test_cancel_subscription(db_session, subscription_service, test_subscription):
    """Test subscription cancellation"""
    canceled = await subscription_service.cancel(db_session, test_subscription.id)
    assert canceled.status == SubscriptionStatus.CANCELED

@pytest.mark.asyncio
async def test_update_subscription_plan(db_session, subscription_service, test_subscription):
    """Test changing subscription plan"""
    updated = await subscription_service.change_plan(
        db_session,
        test_subscription.id,
        new_plan_id="enterprise"
    )
    assert updated.plan_id == "enterprise"

@pytest.mark.asyncio
async def test_get_active_subscriptions(db_session, subscription_service, test_organization):
    """Test fetching active subscriptions"""
    # Create 2 subscriptions (1 active, 1 canceled)
    sub1 = await subscription_service.create(db_session, test_organization.id, "pro", "sub_1")
    sub2 = await subscription_service.create(db_session, test_organization.id, "basic", "sub_2")
    await subscription_service.cancel(db_session, sub2.id)
    
    active = await subscription_service.get_active_subscriptions(db_session, test_organization.id)
    assert len(active) == 1
    assert active[0].id == sub1.id

@pytest.mark.asyncio
async def test_handle_subscription_expired(db_session, subscription_service, test_subscription):
    """Test marking subscription as expired"""
    expired = await subscription_service.mark_expired(db_session, test_subscription.id)
    assert expired.status == SubscriptionStatus.EXPIRED

@pytest.mark.asyncio
async def test_calculate_prorated_amount(subscription_service):
    """Test proration calculation for plan change"""
    # Pro plan: $49/month, 15 days used (50%)
    prorated = subscription_service.calculate_proration(
        current_plan_price=49.00,
        new_plan_price=99.00,
        days_used=15,
        days_in_period=30
    )
    # Should charge difference for remaining 15 days
    # ($99 - $49) * (15/30) = $25
    assert prorated == 25.00
