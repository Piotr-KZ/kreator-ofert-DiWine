import pytest
from unittest.mock import AsyncMock, patch
from app.services.stripe_service import StripeService

@pytest.fixture
def stripe_service():
    return StripeService()

@pytest.mark.asyncio
@patch('stripe.Customer.create')
async def test_create_customer(mock_create, stripe_service, test_organization):
    """Test Stripe customer creation"""
    mock_create.return_value = {"id": "cus_123", "email": "test@org.com"}
    
    customer = await stripe_service.create_customer(
        email=test_organization.email,
        name=test_organization.name,
        metadata={"organization_id": test_organization.id}
    )
    assert customer["id"] == "cus_123"

@pytest.mark.asyncio
@patch('stripe.Subscription.create')
async def test_create_subscription(mock_create, stripe_service):
    """Test Stripe subscription creation"""
    mock_create.return_value = {
        "id": "sub_123",
        "status": "active",
        "current_period_end": 1735689600
    }
    
    subscription = await stripe_service.create_subscription(
        customer_id="cus_123",
        price_id="price_pro"
    )
    assert subscription["id"] == "sub_123"

@pytest.mark.asyncio
@patch('stripe.Subscription.delete')
async def test_cancel_subscription(mock_delete, stripe_service):
    """Test Stripe subscription cancellation"""
    mock_delete.return_value = {"id": "sub_123", "status": "canceled"}
    
    result = await stripe_service.cancel_subscription("sub_123")
    assert result["status"] == "canceled"

@pytest.mark.asyncio
async def test_handle_webhook_payment_succeeded(stripe_service, db_session):
    """Test webhook handling - payment succeeded"""
    event = {
        "type": "invoice.payment_succeeded",
        "data": {
            "object": {
                "id": "in_123",
                "subscription": "sub_123",
                "amount_paid": 9900,
                "status": "paid"
            }
        }
    }
    
    await stripe_service.handle_webhook(db_session, event)
    
    # Verify invoice updated in DB
    from app.services.invoice_service import InvoiceService
    invoice_service = InvoiceService()
    invoice = await invoice_service.get_by_stripe_id(db_session, "in_123")
    assert invoice.status == "paid"

@pytest.mark.asyncio
async def test_handle_webhook_payment_failed(stripe_service, db_session):
    """Test webhook handling - payment failed"""
    event = {
        "type": "invoice.payment_failed",
        "data": {
            "object": {
                "id": "in_123",
                "status": "open"
            }
        }
    }
    
    await stripe_service.handle_webhook(db_session, event)
    
    # Verify invoice marked as failed
    from app.services.invoice_service import InvoiceService
    invoice_service = InvoiceService()
    invoice = await invoice_service.get_by_stripe_id(db_session, "in_123")
    assert invoice.status == "failed"

@pytest.mark.asyncio
@patch('stripe.PaymentIntent.create')
async def test_create_payment_intent(mock_create, stripe_service):
    """Test creating one-time payment intent"""
    mock_create.return_value = {
        "id": "pi_123",
        "client_secret": "secret_123",
        "status": "requires_payment_method"
    }
    
    intent = await stripe_service.create_payment_intent(
        amount=10000,  # $100.00
        currency="usd",
        customer_id="cus_123"
    )
    assert intent["id"] == "pi_123"
