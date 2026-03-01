"""
WebSocket endpoint.
URL: /ws/{organization_id} lub /ws

Klient laczy sie z tokenem JWT w query string:
ws://localhost:8000/ws/org-uuid?token=eyJhbG...

Protokol wiadomosci:
{"type": "ping"}  ->  {"type": "pong"}
"""

from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from fasthub_core.realtime.manager import get_connection_manager

router = APIRouter(tags=["WebSocket"])


def _authenticate_token(token: Optional[str]) -> Optional[str]:
    """Weryfikuj JWT token i zwroc user_id."""
    if not token:
        return None
    try:
        from fasthub_core.auth.service import decode_access_token
        payload = decode_access_token(token)
        if payload:
            return payload.get("sub")
    except Exception:
        pass
    return None


@router.websocket("/ws/{organization_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    organization_id: str,
    token: Optional[str] = Query(None),
):
    """Glowny endpoint WebSocket z organizacja."""
    manager = get_connection_manager()

    user_id = _authenticate_token(token)
    if not user_id:
        await websocket.close(code=4001, reason="Authentication required")
        return

    await manager.connect(websocket, user_id=user_id, organization_id=organization_id)

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception:
        await manager.disconnect(websocket)


@router.websocket("/ws")
async def websocket_endpoint_no_org(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
):
    """WebSocket bez organizacji (np. Super Admin dashboard)."""
    manager = get_connection_manager()

    user_id = _authenticate_token(token)
    if not user_id:
        await websocket.close(code=4001, reason="Authentication required")
        return

    await manager.connect(websocket, user_id=user_id)

    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except (WebSocketDisconnect, Exception):
        await manager.disconnect(websocket)
