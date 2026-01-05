import pytest
from unittest.mock import AsyncMock, patch
from app.services.email_service import EmailService

@pytest.fixture
def email_service():
    return EmailService()

@pytest.mark.asyncio
@patch('app.services.email_service.send_email_async')
async def test_send_welcome_email(mock_send, email_service, test_user):
    """Test sending welcome email"""
    mock_send.return_value = True
    
    result = await email_service.send_welcome_email(
        to=test_user.email,
        name=test_user.full_name
    )
    assert result is True
    mock_send.assert_called_once()

@pytest.mark.asyncio
@patch('app.services.email_service.send_email_async')
async def test_send_password_reset_email(mock_send, email_service, test_user):
    """Test sending password reset email"""
    mock_send.return_value = True
    
    result = await email_service.send_password_reset(
        to=test_user.email,
        reset_token="abc123def456"
    )
    assert result is True

@pytest.mark.asyncio
@patch('app.services.email_service.send_email_async')
async def test_send_invitation_email(mock_send, email_service, test_invitation):
    """Test sending team invitation email"""
    mock_send.return_value = True
    
    result = await email_service.send_invitation(
        to=test_invitation.email,
        organization_name="Test Corp",
        invitation_token=test_invitation.token
    )
    assert result is True

@pytest.mark.asyncio
@patch('app.services.email_service.send_email_async')
async def test_send_invoice_email(mock_send, email_service, test_invoice):
    """Test sending invoice email"""
    mock_send.return_value = True
    
    result = await email_service.send_invoice(
        to="billing@org.com",
        invoice_id=test_invoice.id,
        amount=99.00,
        pdf_attachment=b"fake pdf bytes"
    )
    assert result is True
