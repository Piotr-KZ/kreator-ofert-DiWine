# ============================================================================

import pytest
from app.models.audit_log import AuditLog, AuditAction


@pytest.mark.asyncio
async def test_audit_log_creation():
    """Test audit log entry is created with all fields"""
    log = AuditLog(
        id=uuid4(),
        user_id=uuid4(),
        organization_id=uuid4(),
        action=AuditAction.USER_LOGIN,
        resource_type="user",
        resource_id=uuid4(),
        details={"ip_address": "192.168.1.1"},
        ip_address="192.168.1.1"
    )
    
    assert log.action == AuditAction.USER_LOGIN
    assert log.resource_type == "user"
    assert "ip_address" in log.details
    assert log.created_at is not None


@pytest.mark.asyncio
async def test_audit_log_query_by_user():
    """Test querying audit logs by user_id"""
    from unittest.mock import AsyncMock, MagicMock
    
    user_id = uuid4()
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = [
        AuditLog(id=uuid4(), user_id=user_id, action=AuditAction.USER_LOGIN),
        AuditLog(id=uuid4(), user_id=user_id, action=AuditAction.USER_LOGOUT)
    ]
    mock_db.execute.return_value = mock_result
    
    from app.services.audit_service import get_logs_by_user
    logs = await get_logs_by_user(mock_db, user_id)
    
    assert len(logs) == 2
    assert all(log.user_id == user_id for log in logs)


@pytest.mark.asyncio
async def test_audit_log_query_by_action():
    """Test querying audit logs by action type"""
    from unittest.mock import AsyncMock, MagicMock
    
    action = AuditAction.MEMBER_ADDED
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = [
        AuditLog(id=uuid4(), user_id=uuid4(), action=action),
        AuditLog(id=uuid4(), user_id=uuid4(), action=action)
    ]
    mock_db.execute.return_value = mock_result
    
    from app.services.audit_service import get_logs_by_action
    logs = await get_logs_by_action(mock_db, action)
    
    assert len(logs) == 2
    assert all(log.action == action for log in logs)
