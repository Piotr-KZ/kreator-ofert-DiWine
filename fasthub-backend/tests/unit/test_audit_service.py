import pytest
from app.services.audit_service import AuditService
from app.models.audit_log import AuditLog, AuditAction

@pytest.fixture
def audit_service():
    return AuditService()

@pytest.mark.asyncio
async def test_log_user_action(db_session, audit_service, test_user, test_organization):
    """Test logging user action"""
    log = await audit_service.log_action(
        db_session,
        user_id=test_user.id,
        organization_id=test_organization.id,
        action=AuditAction.USER_LOGIN,
        resource_type="user",
        resource_id=test_user.id,
        changes={"ip": "192.168.1.1"}
    )
    assert log.action == AuditAction.USER_LOGIN
    assert log.changes["ip"] == "192.168.1.1"

@pytest.mark.asyncio
async def test_log_admin_action(db_session, audit_service, test_admin, test_organization):
    """Test logging admin action"""
    log = await audit_service.log_action(
        db_session,
        user_id=test_admin.id,
        organization_id=test_organization.id,
        action=AuditAction.ORGANIZATION_SETTINGS_UPDATED,
        resource_type="organization",
        resource_id=test_organization.id,
        changes={"name": {"old": "Old Name", "new": "New Name"}}
    )
    assert log.changes["name"]["new"] == "New Name"

@pytest.mark.asyncio
async def test_get_audit_logs_by_user(db_session, audit_service, test_user):
    """Test fetching audit logs for specific user"""
    # Create 3 logs
    for i in range(3):
        await audit_service.log_action(
            db_session, test_user.id, 1, AuditAction.USER_LOGIN, "user", test_user.id
        )
    
    logs = await audit_service.get_logs_by_user(db_session, test_user.id, limit=10)
    assert len(logs) == 3

@pytest.mark.asyncio
async def test_get_audit_logs_by_resource(db_session, audit_service, test_user):
    """Test fetching audit logs for specific resource"""
    # Log 2 actions on same resource
    await audit_service.log_action(
        db_session, test_user.id, 1, AuditAction.USER_UPDATED, "user", 123
    )
    await audit_service.log_action(
        db_session, test_user.id, 1, AuditAction.USER_DELETED, "user", 123
    )
    
    logs = await audit_service.get_logs_by_resource(
        db_session, resource_type="user", resource_id=123
    )
    assert len(logs) == 2

@pytest.mark.asyncio
async def test_filter_audit_logs_by_date(db_session, audit_service, test_user):
    """Test filtering audit logs by date range"""
    import datetime
    
    # Create log
    log = await audit_service.log_action(
        db_session, test_user.id, 1, AuditAction.USER_LOGIN, "user", test_user.id
    )
    
    # Filter last 7 days
    start = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    end = datetime.datetime.utcnow()
    
    logs = await audit_service.get_logs_by_date_range(db_session, start, end)
    assert len(logs) >= 1
    assert log.id in [l.id for l in logs]
