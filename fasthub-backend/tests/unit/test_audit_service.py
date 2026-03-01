"""
Unit tests for Audit Service
"""

import pytest
import uuid
from unittest.mock import Mock
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.organization import Organization
from app.services.audit_service import AuditService


@pytest.fixture
def audit_service(db_session: AsyncSession) -> AuditService:
    """Create Audit Service instance"""
    return AuditService(db=db_session)


@pytest.mark.asyncio
async def test_log_action_basic(
    audit_service: AuditService,
    test_user: User,
    db_session: AsyncSession
):
    """Test logging a basic action"""
    # Act
    audit_log = await audit_service.log_action(
        user=test_user,
        action="user.update",
        resource_type="user",
        resource_id=test_user.id
    )
    await db_session.commit()
    
    # Assert
    assert audit_log.user_id == test_user.id
    assert audit_log.action == "user.update"
    assert audit_log.resource_type == "user"
    assert audit_log.resource_id == str(test_user.id)
    assert audit_log.extra_data is None
    assert audit_log.ip_address is None
    assert audit_log.user_agent is None


@pytest.mark.asyncio
async def test_log_action_with_details(
    audit_service: AuditService,
    test_user: User,
    db_session: AsyncSession
):
    """Test logging action with details"""
    # Arrange
    details = {
        "old_value": "test@example.com",
        "new_value": "newemail@example.com",
        "field": "email"
    }
    
    # Act
    audit_log = await audit_service.log_action(
        user=test_user,
        action="user.update",
        resource_type="user",
        resource_id=test_user.id,
        extra_data=details
    )
    await db_session.commit()
    
    # Assert
    assert audit_log.extra_data == details
    assert audit_log.extra_data["field"] == "email"


@pytest.mark.asyncio
async def test_log_action_with_request(
    audit_service: AuditService,
    test_user: User,
    db_session: AsyncSession
):
    """Test logging action with request metadata"""
    # Arrange - Mock FastAPI Request
    mock_request = Mock()
    mock_request.client = Mock()
    mock_request.client.host = "192.168.1.1"
    mock_request.headers = {"user-agent": "Mozilla/5.0"}
    
    # Act
    audit_log = await audit_service.log_action(
        user=test_user,
        action="organization.delete",
        resource_type="organization",
        resource_id=uuid.UUID('00000000-0000-0000-0000-000000000001'),
        request=mock_request
    )
    await db_session.commit()
    
    # Assert
    assert audit_log.ip_address == "192.168.1.1"
    assert audit_log.user_agent == "Mozilla/5.0"


@pytest.mark.asyncio
async def test_log_action_without_resource_id(
    audit_service: AuditService,
    test_user: User,
    db_session: AsyncSession
):
    """Test logging action without resource ID"""
    # Act
    audit_log = await audit_service.log_action(
        user=test_user,
        action="system.backup",
        resource_type="system"
    )
    await db_session.commit()
    
    # Assert
    assert audit_log.resource_id is None
    assert audit_log.action == "system.backup"
    assert audit_log.resource_type == "system"


@pytest.mark.asyncio
async def test_log_multiple_actions(
    audit_service: AuditService,
    test_user: User,
    db_session: AsyncSession
):
    """Test logging multiple actions"""
    # Act
    log1 = await audit_service.log_action(
        user=test_user,
        action="user.login",
        resource_type="user",
        resource_id=test_user.id
    )
    
    log2 = await audit_service.log_action(
        user=test_user,
        action="organization.create",
        resource_type="organization"
    )
    await db_session.commit()
    
    # Assert
    assert log1.user_id == test_user.id
    assert log1.action == "user.login"
    assert log2.user_id == test_user.id
    assert log2.action == "organization.create"
    assert log1.id != log2.id


@pytest.mark.asyncio
async def test_log_action_request_without_client(
    audit_service: AuditService,
    test_user: User,
    db_session: AsyncSession
):
    """Test logging with request but no client info"""
    # Arrange - Mock request without client
    mock_request = Mock()
    mock_request.client = None
    mock_request.headers = {"user-agent": "TestAgent/1.0"}
    
    # Act
    audit_log = await audit_service.log_action(
        user=test_user,
        action="user.update",
        resource_type="user",
        resource_id=test_user.id,
        request=mock_request
    )
    await db_session.commit()
    
    # Assert
    assert audit_log.ip_address is None
    assert audit_log.user_agent == "TestAgent/1.0"


@pytest.mark.asyncio
async def test_log_action_complex_details(
    audit_service: AuditService,
    test_user: User,
    db_session: AsyncSession
):
    """Test logging action with complex nested details"""
    # Arrange
    complex_details = {
        "operation": "bulk_update",
        "affected_users": [str(test_user.id)],
        "changes": {
            "role": {"from": "user", "to": "admin"},
            "permissions": ["read", "write", "delete"]
        },
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    # Act
    audit_log = await audit_service.log_action(
        user=test_user,
        action="user.bulk_update",
        resource_type="user",
        extra_data=complex_details
    )
    await db_session.commit()
    
    # Assert
    assert audit_log.extra_data["operation"] == "bulk_update"
    assert len(audit_log.extra_data["affected_users"]) == 1
    assert audit_log.extra_data["changes"]["role"]["to"] == "admin"
