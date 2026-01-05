import pytest
from app.services.permission_service import PermissionService
from app.models.permission import Permission
from app.models.role import Role

@pytest.fixture
def permission_service():
    return PermissionService()

@pytest.mark.asyncio
async def test_create_permission(db_session, permission_service):
    """Test creating permission"""
    perm = await permission_service.create(
        db_session,
        name="manage_workflows",
        category="workflows",
        description="Can create and delete workflows"
    )
    assert perm.name == "manage_workflows"

@pytest.mark.asyncio
async def test_assign_permission_to_role(db_session, permission_service, test_role, test_permission):
    """Test assigning permission to role"""
    await permission_service.assign_to_role(
        db_session,
        role_id=test_role.id,
        permission_id=test_permission.id
    )
    
    # Verify
    role_perms = await permission_service.get_role_permissions(db_session, test_role.id)
    assert test_permission.id in [p.id for p in role_perms]

@pytest.mark.asyncio
async def test_remove_permission_from_role(db_session, permission_service, test_role, test_permission):
    """Test removing permission from role"""
    await permission_service.assign_to_role(db_session, test_role.id, test_permission.id)
    await permission_service.remove_from_role(db_session, test_role.id, test_permission.id)
    
    role_perms = await permission_service.get_role_permissions(db_session, test_role.id)
    assert test_permission.id not in [p.id for p in role_perms]

@pytest.mark.asyncio
async def test_check_user_permission(db_session, permission_service, test_user, test_organization):
    """Test checking if user has specific permission"""
    # Assume test_user has role with "manage_users" permission
    has_perm = await permission_service.user_has_permission(
        db_session,
        user_id=test_user.id,
        organization_id=test_organization.id,
        permission_name="manage_users"
    )
    assert has_perm is True  # or False depending on test setup

@pytest.mark.asyncio
async def test_list_all_permissions(db_session, permission_service):
    """Test listing all system permissions"""
    permissions = await permission_service.list_all(db_session)
    assert len(permissions) > 0  # Should have default permissions
