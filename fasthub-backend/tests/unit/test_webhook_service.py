import pytest
from app.services.webhook_service import WebhookService
from app.models.webhook import Webhook, WebhookEvent

@pytest.fixture
def webhook_service():
    return WebhookService()

@pytest.mark.asyncio
async def test_create_webhook(db_session, webhook_service, test_organization):
    """Test creating webhook"""
    webhook = await webhook_service.create(
        db_session,
        organization_id=test_organization.id,
        url="https://api.example.com/webhooks",
        events=[WebhookEvent.USER_CREATED, WebhookEvent.SUBSCRIPTION_UPDATED],
        secret="whsec_123"
    )
    assert webhook.url == "https://api.example.com/webhooks"
    assert len(webhook.events) == 2

@pytest.mark.asyncio
@patch('httpx.AsyncClient.post')
async def test_trigger_webhook(mock_post, webhook_service, test_webhook):
    """Test triggering webhook"""
    mock_post.return_value.status_code = 200
    
    result = await webhook_service.trigger(
        webhook=test_webhook,
        event=WebhookEvent.USER_CREATED,
        payload={"user_id": 123, "email": "new@user.com"}
    )
    assert result.success is True

@pytest.mark.asyncio
async def test_verify_webhook_signature(webhook_service):
    """Test webhook signature verification"""
    payload = '{"event": "user.created", "data": {}}'
    secret = "whsec_abc123"
    
    signature = webhook_service.generate_signature(payload, secret)
    is_valid = webhook_service.verify_signature(payload, signature, secret)
    assert is_valid is True

@pytest.mark.asyncio
async def test_webhook_retry_logic(webhook_service, test_webhook):
    """Test webhook retry on failure"""
    # Mock 3 failures then success
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.side_effect = [
            Exception("Connection failed"),
            Exception("Timeout"),
            Exception("Server error"),
            AsyncMock(status_code=200)
        ]
        
        result = await webhook_service.trigger_with_retry(
            webhook=test_webhook,
            event=WebhookEvent.SUBSCRIPTION_UPDATED,
            payload={},
            max_retries=3
        )
        assert result.success is True
        assert result.attempts == 4
