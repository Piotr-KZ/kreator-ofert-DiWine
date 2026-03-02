"""
Testy Multi-tenancy — context, middleware, dependencies, scoped queries, CLI.
"""

import pytest
from uuid import uuid4, UUID
from unittest.mock import MagicMock, AsyncMock, patch


# ============================================================================
# TENANT CONTEXT
# ============================================================================

class TestTenantContext:

    def test_context_dataclass(self):
        from fasthub_core.tenancy.context import TenantContext
        ctx = TenantContext(
            tenant_id=uuid4(),
            tenant_slug="test-firma",
            tenant_name="Test Firma",
            user_id=uuid4(),
            user_role="admin",
        )
        assert ctx.tenant_slug == "test-firma"
        assert ctx.user_role == "admin"

    def test_default_is_none(self):
        from fasthub_core.tenancy.context import get_current_tenant, get_current_tenant_id
        from fasthub_core.tenancy.context import clear_tenant_context
        clear_tenant_context()
        assert get_current_tenant() is None
        assert get_current_tenant_id() is None

    def test_set_and_get(self):
        from fasthub_core.tenancy.context import (
            TenantContext, set_current_tenant, get_current_tenant,
            get_current_tenant_id, clear_tenant_context,
        )
        tid = uuid4()
        ctx = TenantContext(tenant_id=tid, tenant_slug="firma", user_role="admin")
        set_current_tenant(ctx)

        assert get_current_tenant() is ctx
        assert get_current_tenant_id() == tid

        clear_tenant_context()
        assert get_current_tenant() is None

    def test_clear(self):
        from fasthub_core.tenancy.context import (
            TenantContext, set_current_tenant, clear_tenant_context, get_current_tenant,
        )
        set_current_tenant(TenantContext(tenant_id=uuid4()))
        clear_tenant_context()
        assert get_current_tenant() is None

    def test_context_defaults(self):
        from fasthub_core.tenancy.context import TenantContext
        ctx = TenantContext(tenant_id=uuid4())
        assert ctx.tenant_slug == ""
        assert ctx.tenant_name == ""
        assert ctx.user_id is None
        assert ctx.user_role == ""


# ============================================================================
# TENANT MIDDLEWARE
# ============================================================================

class TestTenantMiddleware:

    def test_class_exists(self):
        from fasthub_core.tenancy.middleware import TenantMiddleware
        assert TenantMiddleware is not None

    def test_default_excluded_paths(self):
        from fasthub_core.tenancy.middleware import DEFAULT_EXCLUDED_PATHS
        assert "/health" in DEFAULT_EXCLUDED_PATHS
        assert "/docs" in DEFAULT_EXCLUDED_PATHS
        assert "/auth/login" in DEFAULT_EXCLUDED_PATHS
        assert "/billing/webhooks" in DEFAULT_EXCLUDED_PATHS

    def test_is_excluded(self):
        from fasthub_core.tenancy.middleware import TenantMiddleware
        mw = TenantMiddleware(app=MagicMock())
        assert mw._is_excluded("/health") == True
        assert mw._is_excluded("/docs") == True
        assert mw._is_excluded("/api/processes") == False
        assert mw._is_excluded("/auth/login") == True

    def test_custom_excluded_paths(self):
        from fasthub_core.tenancy.middleware import TenantMiddleware
        mw = TenantMiddleware(app=MagicMock(), excluded_paths=["/public", "/health"])
        assert mw._is_excluded("/public/page") == True
        assert mw._is_excluded("/api/data") == False

    def test_is_excluded_prefix_match(self):
        from fasthub_core.tenancy.middleware import TenantMiddleware
        mw = TenantMiddleware(app=MagicMock())
        assert mw._is_excluded("/health/ready") == True
        assert mw._is_excluded("/auth/login/magic") == True
        assert mw._is_excluded("/auth/register/confirm") == True


# ============================================================================
# TENANT DEPENDENCIES
# ============================================================================

class TestTenantDependencies:

    @pytest.mark.asyncio
    async def test_require_tenant_without_context(self):
        from fasthub_core.tenancy.context import clear_tenant_context
        from fasthub_core.tenancy.dependencies import require_tenant
        from fastapi import HTTPException

        clear_tenant_context()
        with pytest.raises(HTTPException) as exc_info:
            await require_tenant()
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_require_tenant_with_context(self):
        from fasthub_core.tenancy.context import TenantContext, set_current_tenant, clear_tenant_context
        from fasthub_core.tenancy.dependencies import require_tenant

        tid = uuid4()
        set_current_tenant(TenantContext(tenant_id=tid, user_role="admin"))
        result = await require_tenant()
        assert result.tenant_id == tid
        clear_tenant_context()

    @pytest.mark.asyncio
    async def test_require_tenant_admin_with_viewer(self):
        from fasthub_core.tenancy.context import TenantContext, set_current_tenant, clear_tenant_context
        from fasthub_core.tenancy.dependencies import require_tenant_admin
        from fastapi import HTTPException

        set_current_tenant(TenantContext(tenant_id=uuid4(), user_role="viewer"))
        with pytest.raises(HTTPException) as exc_info:
            await require_tenant_admin()
        assert exc_info.value.status_code == 403
        clear_tenant_context()

    @pytest.mark.asyncio
    async def test_require_tenant_admin_with_admin(self):
        from fasthub_core.tenancy.context import TenantContext, set_current_tenant, clear_tenant_context
        from fasthub_core.tenancy.dependencies import require_tenant_admin

        set_current_tenant(TenantContext(tenant_id=uuid4(), user_role="admin"))
        result = await require_tenant_admin()
        assert result.user_role == "admin"
        clear_tenant_context()

    @pytest.mark.asyncio
    async def test_require_tenant_admin_with_owner(self):
        from fasthub_core.tenancy.context import TenantContext, set_current_tenant, clear_tenant_context
        from fasthub_core.tenancy.dependencies import require_tenant_admin

        set_current_tenant(TenantContext(tenant_id=uuid4(), user_role="owner"))
        result = await require_tenant_admin()
        assert result.user_role == "owner"
        clear_tenant_context()


# ============================================================================
# SCOPED QUERIES
# ============================================================================

class TestScopedQueries:

    def test_tenant_query_without_context_raises(self):
        from fasthub_core.tenancy.scoped import tenant_query
        from fasthub_core.tenancy.context import clear_tenant_context
        from sqlalchemy import select

        clear_tenant_context()
        with pytest.raises(ValueError):
            tenant_query(select(), None)

    def test_optional_tenant_query_without_context(self):
        from fasthub_core.tenancy.scoped import optional_tenant_query
        from fasthub_core.tenancy.context import clear_tenant_context
        from sqlalchemy import select

        clear_tenant_context()
        query = select()
        result = optional_tenant_query(query, None)
        assert result is query

    def test_tenant_query_callable(self):
        from fasthub_core.tenancy.scoped import tenant_query, optional_tenant_query
        assert callable(tenant_query)
        assert callable(optional_tenant_query)

    def test_tenant_query_with_context(self):
        from fasthub_core.tenancy.scoped import tenant_query
        from fasthub_core.tenancy.context import TenantContext, set_current_tenant, clear_tenant_context
        from sqlalchemy import select, column

        tid = uuid4()
        set_current_tenant(TenantContext(tenant_id=tid))
        # Use raw column to avoid mapper initialization issues
        org_id_col = column("organization_id")
        query = tenant_query(select(org_id_col), org_id_col)
        compiled = str(query)
        assert "WHERE" in compiled
        clear_tenant_context()

    def test_optional_tenant_query_with_context(self):
        from fasthub_core.tenancy.scoped import optional_tenant_query
        from fasthub_core.tenancy.context import TenantContext, set_current_tenant, clear_tenant_context
        from sqlalchemy import select, column

        tid = uuid4()
        set_current_tenant(TenantContext(tenant_id=tid))
        org_id_col = column("organization_id")
        query = optional_tenant_query(select(org_id_col), org_id_col)
        compiled = str(query)
        assert "WHERE" in compiled
        clear_tenant_context()


# ============================================================================
# CLI
# ============================================================================

class TestCLI:

    def test_app_exists(self):
        from fasthub_core.cli import app
        assert app is not None

    def test_app_has_commands(self):
        from fasthub_core.cli.app import app
        import fasthub_core.cli.commands

        # Typer stores callback names, not display names
        callback_names = [cmd.callback.__name__ for cmd in app.registered_commands if cmd.callback]
        assert "seed" in callback_names
        assert "create_admin" in callback_names
        assert "check" in callback_names
        assert "show_config" in callback_names
        assert "shell" in callback_names

    def test_entry_point(self):
        from fasthub_core.cli.entry import main
        assert callable(main)

    def test_app_name(self):
        from fasthub_core.cli.app import app
        assert app.info.name == "fasthub"

    def test_app_no_args_is_help(self):
        from fasthub_core.cli.app import app
        assert app.info.no_args_is_help == True


# ============================================================================
# DB SESSION CONTEXT MANAGER
# ============================================================================

class TestDBSession:

    def test_get_db_session_exists(self):
        from fasthub_core.db.session import get_db_session
        assert callable(get_db_session)

    def test_init_db_exists(self):
        from fasthub_core.db.session import init_db
        assert callable(init_db)


# ============================================================================
# EXPORTS
# ============================================================================

class TestExports:

    def test_tenancy_exports(self):
        from fasthub_core.tenancy import (
            get_current_tenant, get_current_tenant_id,
            set_current_tenant, clear_tenant_context,
            TenantContext, TenantMiddleware,
            require_tenant, require_tenant_admin, get_tenant_db,
        )
        assert TenantMiddleware is not None
        assert callable(get_current_tenant)
        assert callable(require_tenant)

    def test_cli_export(self):
        from fasthub_core.cli import app
        assert app is not None

    def test_main_init_exports(self):
        from fasthub_core import TenantMiddleware, get_current_tenant
        assert TenantMiddleware is not None

    def test_middleware_init_exports(self):
        from fasthub_core.middleware import TenantMiddleware
        assert TenantMiddleware is not None
