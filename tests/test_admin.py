"""Testy Super Admin"""


def test_admin_router_exists():
    """Router admin musi istnieć i mieć prefix /api/admin"""
    from fasthub_core.admin.routes import router
    assert router is not None
    assert router.prefix == "/api/admin"


def test_admin_schemas():
    """Schemas admin muszą być importowalne i poprawne"""
    from fasthub_core.admin.schemas import (
        OrganizationStats, OrganizationList, UserDetail,
        UserList, ImpersonateRequest, SystemStats
    )
    # ImpersonateRequest wymaga reason
    req = ImpersonateRequest(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        reason="Klient zgłosił problem z logowaniem"
    )
    assert req.reason == "Klient zgłosił problem z logowaniem"


def test_admin_service_exists():
    """AdminService musi być importowalny"""
    from fasthub_core.admin.service import AdminService
    assert AdminService is not None


def test_superadmin_dependency():
    """require_superadmin musi być callable"""
    from fasthub_core.auth.superadmin import require_superadmin
    assert callable(require_superadmin)


def test_admin_routes_count():
    """Powinno być 5 endpointów admin"""
    from fasthub_core.admin.routes import router
    routes = [r for r in router.routes]
    assert len(routes) >= 5  # stats, orgs list, org detail, users, impersonate


def test_user_model_has_superadmin_field():
    """Model User musi mieć pole is_superadmin"""
    from fasthub_core.users.models import User
    assert hasattr(User, 'is_superadmin')


def test_admin_importable_from_init():
    """admin_router musi być dostępny z fasthub_core"""
    from fasthub_core import admin_router
    assert admin_router is not None


def test_impersonate_request_requires_reason():
    """ImpersonateRequest bez reason powinien rzucić błąd"""
    import pytest
    from fasthub_core.admin.schemas import ImpersonateRequest

    with pytest.raises(Exception):
        ImpersonateRequest(
            user_id="550e8400-e29b-41d4-a716-446655440000"
            # brak reason — powinien być wymagany
        )


def test_system_stats_schema():
    """SystemStats musi akceptować poprawne dane"""
    from fasthub_core.admin.schemas import SystemStats

    stats = SystemStats(
        total_organizations=10,
        total_users=50,
        active_users_last_30_days=30,
        total_subscriptions_active=5,
        organizations_by_plan={"free": 7, "pro": 3}
    )
    assert stats.total_organizations == 10
    assert stats.organizations_by_plan["pro"] == 3
