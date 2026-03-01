"""
Helper do wyciągania IP i User-Agent z FastAPI request.
Używane przez AuditService żeby automatycznie logować skąd przyszła zmiana.

Użycie w endpoincie:
    from fasthub_core.audit.request_context import get_request_context

    @router.put("/settings")
    async def update_settings(request: Request, ...):
        ctx = get_request_context(request)
        await audit.log_action(
            ...,
            ip_address=ctx["ip_address"],
            user_agent=ctx["user_agent"],
        )
"""

from fastapi import Request
from typing import Dict, Optional


def get_request_context(request: Request) -> Dict[str, Optional[str]]:
    """Wyciąga IP i User-Agent z request"""
    # IP: sprawdź X-Forwarded-For (jeśli za proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        ip_address = forwarded_for.split(",")[0].strip()
    else:
        ip_address = request.client.host if request.client else None

    user_agent = request.headers.get("User-Agent")

    return {
        "ip_address": ip_address,
        "user_agent": user_agent,
    }
