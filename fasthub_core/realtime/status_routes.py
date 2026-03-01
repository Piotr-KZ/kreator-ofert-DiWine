"""REST endpointy do sprawdzania statusu WebSocket."""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from fasthub_core.auth.dependencies import get_current_user
from fasthub_core.realtime.manager import get_connection_manager

router = APIRouter(prefix="/api/realtime", tags=["Realtime"])


@router.get("/status")
async def get_realtime_status(current_user=Depends(get_current_user)):
    """Statystyki polaczen WebSocket."""
    manager = get_connection_manager()
    return manager.get_connection_count()


@router.get("/online-users")
async def get_online_users(
    organization_id: Optional[str] = Query(None),
    current_user=Depends(get_current_user),
):
    """Lista online userow (opcjonalnie w organizacji)."""
    manager = get_connection_manager()
    users = manager.get_online_users(organization_id)
    return {"online_users": users, "count": len(users)}
