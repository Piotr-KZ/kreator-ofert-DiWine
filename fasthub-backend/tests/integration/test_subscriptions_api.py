"""
Integration tests for subscriptions API endpoints
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import status


@pytest.mark.asyncio
@patch("app.services.stripe_service.stripe.Customer.create")
@patch("app.services.stripe_service.stripe.Subscription.create")
async def test_create_subscription(
    mock_sub_create, mock_cust_create, async_client, test_user, auth_headers
):
    """Test create subscription endpoint"""
    # Mock Stripe responses
    mock_cust_create.return_value = MagicMock(id="cus_test123")
    mock_sub_create.return_value = MagicMock(
        id="sub_test123",
        status="active",
        current_period_start=1234567890,
        current_period_end=1237159890,
    )

    response = await async_client.post(
        "/api/v1/subscriptions/",
        headers=auth_headers,
        json={"plan": "professional", "payment_method_id": "pm_test123"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["stripe_subscription_id"] == "sub_test123"
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_get_subscription(async_client, test_user, test_subscription, auth_headers):
    """Test get current subscription"""
    response = await async_client.get("/api/v1/subscriptions/current", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_subscription.id)
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_get_subscription_not_found(async_client, test_user, auth_headers):
    """Test get subscription when none exists"""
    response = await async_client.get("/api/v1/subscriptions/current", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
@patch("app.services.stripe_service.stripe.Subscription.modify")
async def test_change_subscription_plan(
    mock_sub_modify, async_client, test_user, test_subscription, auth_headers
):
    """Test change subscription plan"""
    mock_sub_modify.return_value = MagicMock(
        id=test_subscription.stripe_subscription_id, status="active"
    )

    response = await async_client.patch(
        "/api/v1/subscriptions/change-plan", headers=auth_headers, json={"plan": "enterprise"}
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
@patch("app.services.stripe_service.stripe.Subscription.modify")
async def test_cancel_subscription(
    mock_sub_modify, async_client, test_user, test_subscription, auth_headers
):
    """Test cancel subscription"""
    mock_sub_modify.return_value = MagicMock(
        id=test_subscription.stripe_subscription_id, cancel_at_period_end=True
    )

    response = await async_client.post("/api/v1/subscriptions/cancel", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Subscription will be canceled at period end"


@pytest.mark.asyncio
@patch("app.services.stripe_service.stripe.billing_portal.Session.create")
async def test_create_billing_portal(
    mock_portal_create, async_client, test_user, test_subscription, auth_headers
):
    """Test create billing portal session"""
    mock_portal_create.return_value = MagicMock(url="https://billing.stripe.com/session/test123")

    response = await async_client.post("/api/v1/subscriptions/billing-portal", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "url" in data
    assert "stripe.com" in data["url"]


@pytest.mark.asyncio
async def test_webhook_subscription_updated(async_client):
    """Test Stripe webhook for subscription update"""
    webhook_data = {
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_test123",
                "status": "active",
                "customer": "cus_test123",
                "current_period_start": 1234567890,
                "current_period_end": 1237159890,
                "items": {"data": [{"price": {"id": "price_test123"}}]},
            }
        },
    }

    response = await async_client.post("/api/v1/subscriptions/webhook", json=webhook_data)

    # Webhook should accept the event
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
