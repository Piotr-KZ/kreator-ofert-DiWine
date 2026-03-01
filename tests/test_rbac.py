"""Testy RBAC"""


def test_rbac_models_exist():
    """Modele Permission, Role, RolePermission, UserRole muszą być importowalne"""
    from fasthub_core.rbac.models import Permission, Role, RolePermission, UserRole
    assert Permission is not None
    assert Role is not None
    assert RolePermission is not None
    assert UserRole is not None


def test_rbac_service_exists():
    """RBACService musi mieć wszystkie wymagane metody"""
    from fasthub_core.rbac.service import RBACService
    assert RBACService is not None
    assert hasattr(RBACService, 'check_permission')
    assert hasattr(RBACService, 'get_user_permissions')
    assert hasattr(RBACService, 'assign_role')
    assert hasattr(RBACService, 'remove_role')
    assert hasattr(RBACService, 'create_custom_role')
    assert hasattr(RBACService, 'update_role_permissions')
    assert hasattr(RBACService, 'delete_role')
    assert hasattr(RBACService, 'list_organization_roles')
    assert hasattr(RBACService, 'list_permissions')
    assert hasattr(RBACService, 'seed_permissions')
    assert hasattr(RBACService, 'seed_organization_roles')
    assert hasattr(RBACService, 'register_app_permissions')


def test_rbac_middleware():
    """require_permission zwraca callable (dependency)"""
    from fasthub_core.rbac.middleware import require_permission
    dep = require_permission("team.view_members")
    assert callable(dep)


def test_rbac_defaults():
    """Domyślne uprawnienia i role muszą istnieć"""
    from fasthub_core.rbac.defaults import CORE_PERMISSIONS, SYSTEM_ROLES
    # Musi mieć minimum te kategorie
    assert "team" in CORE_PERMISSIONS
    assert "billing" in CORE_PERMISSIONS
    assert "settings" in CORE_PERMISSIONS
    assert "audit" in CORE_PERMISSIONS
    # Musi mieć 3 role systemowe
    assert "owner" in SYSTEM_ROLES
    assert "admin" in SYSTEM_ROLES
    assert "member" in SYSTEM_ROLES
    # Owner ma wszystkie permissions
    assert SYSTEM_ROLES["owner"]["permissions"] == "*"
    # Member jest domyślną rolą
    assert SYSTEM_ROLES["member"]["is_default"] == True


def test_rbac_router():
    """Router RBAC musi mieć prefix /api/rbac i minimum 8 endpointów"""
    from fasthub_core.rbac.routes import router
    assert router.prefix == "/api/rbac"
    routes = [r for r in router.routes]
    assert len(routes) >= 8  # permissions, roles CRUD, assign, unassign, user-perms


def test_rbac_schemas():
    """Schemas RBAC muszą być importowalne i poprawne"""
    from fasthub_core.rbac.schemas import (
        PermissionResponse, RoleResponse, RoleCreateRequest,
        RoleUpdateRequest, AssignRoleRequest, UserPermissionsResponse,
    )
    # Test tworzenia roli wymaga name i permissions
    req = RoleCreateRequest(
        name="Kierownik Budowy",
        permissions=["team.view_members", "processes.view", "processes.execute"]
    )
    assert req.name == "Kierownik Budowy"
    assert len(req.permissions) == 3


def test_permission_name_format():
    """Wszystkie permissions muszą mieć format 'category.action'"""
    from fasthub_core.rbac.defaults import CORE_PERMISSIONS
    for category, perms in CORE_PERMISSIONS.items():
        for name, description in perms:
            assert "." in name, f"Brak '.' w permission: {name}"
            assert name.startswith(category + "."), f"Permission {name} nie zaczyna się od {category}."


def test_all_core_permission_names():
    """Musi być minimum 13 bazowych uprawnień"""
    from fasthub_core.rbac.defaults import get_all_core_permission_names
    names = get_all_core_permission_names()
    assert len(names) >= 13
    assert "team.view_members" in names
    assert "billing.change_plan" in names
    assert "settings.edit" in names
    assert "audit.view_log" in names


def test_rbac_importable_from_init():
    """rbac_router, RBACService, require_permission muszą być dostępne z fasthub_core"""
    from fasthub_core import rbac_router, RBACService, require_permission
    assert rbac_router is not None
    assert RBACService is not None
    assert callable(require_permission)


def test_permission_contract_uses_rbac():
    """FastHubPermission musi używać RBACService"""
    from fasthub_core.contracts_impl import FastHubPermission
    import inspect
    source = inspect.getsource(FastHubPermission.check_permission)
    assert "RBACService" in source


def test_assign_role_request_schema():
    """AssignRoleRequest wymaga user_id i role_id"""
    import pytest
    from fasthub_core.rbac.schemas import AssignRoleRequest

    req = AssignRoleRequest(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        role_id="660e8400-e29b-41d4-a716-446655440000",
    )
    assert str(req.user_id) == "550e8400-e29b-41d4-a716-446655440000"

    with pytest.raises(Exception):
        AssignRoleRequest(user_id="550e8400-e29b-41d4-a716-446655440000")
