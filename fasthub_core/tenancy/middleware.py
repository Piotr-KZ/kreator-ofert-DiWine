"""
Tenant Middleware — automatyczna izolacja multi-tenancy.

Dla KAŻDEGO request z JWT:
1. Dekoduj JWT -> wyciągnij user_id
2. Znajdź organizację użytkownika (owner lub member)
3. Ustaw TenantContext w ContextVar
4. Request się wykonuje z dostępnym get_current_tenant()
5. Wyczyść kontekst po zakończeniu

Endpointy publiczne (bez JWT) przechodzą bez tenanta:
- /health, /docs, /openapi.json
- /auth/login, /auth/register
- /billing/webhooks (Stripe callback)

Konfiguracja:
    app.add_middleware(TenantMiddleware, excluded_paths=["/health", "/auth"])
"""

import logging
from typing import List, Optional
from uuid import UUID

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from fasthub_core.tenancy.context import (
    TenantContext,
    set_current_tenant,
    clear_tenant_context,
)

logger = logging.getLogger(__name__)

# Domyślne ścieżki bez tenant context
DEFAULT_EXCLUDED_PATHS = [
    "/health",
    "/ready",
    "/metrics",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/auth/login",
    "/auth/register",
    "/auth/magic-link",
    "/auth/verify",
    "/billing/webhooks",
]


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware automatycznie ustawiający tenant context.

    Użycie:
        app.add_middleware(
            TenantMiddleware,
            excluded_paths=["/custom/public"],
        )
    """

    def __init__(self, app, excluded_paths: Optional[List[str]] = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or DEFAULT_EXCLUDED_PATHS

    async def dispatch(self, request: Request, call_next) -> Response:
        # Sprawdź czy ścieżka jest wykluczona
        path = request.url.path
        if self._is_excluded(path):
            return await call_next(request)

        # Próbuj wyciągnąć tenant z JWT
        try:
            context = await self._resolve_tenant(request)
            if context:
                set_current_tenant(context)
        except Exception as e:
            logger.debug(f"Tenant resolution skipped: {e}")
            # Nie blokuj requestu — auth middleware i tak sprawdzi JWT

        try:
            response = await call_next(request)
            return response
        finally:
            clear_tenant_context()

    def _is_excluded(self, path: str) -> bool:
        """Czy ścieżka jest wykluczona z tenant resolution."""
        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                return True
        return False

    async def _resolve_tenant(self, request: Request) -> Optional[TenantContext]:
        """
        Wyciągnij tenant z JWT -> znajdź organizację.

        Kolejność:
        1. Dekoduj JWT (Authorization: Bearer xxx)
        2. Wyciągnij user_id z payload
        3. Znajdź organizację (owner -> member)
        4. Zwróć TenantContext
        """
        # 1. Wyciągnij token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header.replace("Bearer ", "")

        # 2. Dekoduj JWT
        from fasthub_core.auth.service import decode_access_token
        payload = decode_access_token(token)
        if not payload:
            return None

        user_id_str = payload.get("sub")
        if not user_id_str:
            return None

        user_id = UUID(user_id_str)

        # 3. Znajdź organizację
        from fasthub_core.db.session import get_db_session
        from fasthub_core.users.models import Organization, Member
        from sqlalchemy import select

        async with get_db_session() as db:
            # Priority 1: Owner
            result = await db.execute(
                select(Organization)
                .where(Organization.owner_id == user_id)
                .order_by(Organization.created_at)
                .limit(1)
            )
            org = result.scalar_one_or_none()
            user_role = "admin"

            # Priority 2: Member
            if not org:
                result = await db.execute(
                    select(Member)
                    .where(Member.user_id == user_id)
                    .order_by(Member.joined_at)
                    .limit(1)
                )
                membership = result.scalar_one_or_none()
                if membership:
                    result = await db.execute(
                        select(Organization)
                        .where(Organization.id == membership.organization_id)
                    )
                    org = result.scalar_one_or_none()
                    user_role = membership.role.value if hasattr(membership.role, 'value') else str(membership.role)

            if not org:
                return None

            return TenantContext(
                tenant_id=org.id,
                tenant_slug=org.slug,
                tenant_name=org.name,
                user_id=user_id,
                user_role=user_role,
            )
