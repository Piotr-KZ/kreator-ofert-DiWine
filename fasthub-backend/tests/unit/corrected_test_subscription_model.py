"""Test Subscription model"""
import pytest
from datetime import datetime, timedelta
from app.models.subscription import Subscription

def test_subscription_creation():
    """Test subscription basic fields"""
    sub = Subscription(
        organization_id=1,
        stripe_subscription_id="sub_123",
        stripe_customer_id="cus_123",
        status="active",
        plan_id="pro"
    )
    assert sub.status == "active"
    assert sub.plan_id == "pro"

def test_subscription_default_values():
    """Test default values"""
    sub = Subscription(
        organization_id=1,
        stripe_subscription_id="sub_123",
        status="active",
        plan_id="basic"
    )
    assert sub.cancel_at_period_end is False

def test_subscription_period_dates():
    """Test period start/end dates"""
    now = datetime.utcnow()
    end = now + timedelta(days=30)
    
    sub = Subscription(
        organization_id=1,
        stripe_subscription_id="sub_123",
        status="active",
        plan_id="pro",
        current_period_start=now,
        current_period_end=end
    )
    assert sub.current_period_start == now
    assert sub.current_period_end == end
