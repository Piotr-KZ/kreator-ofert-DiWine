"""
WebSocket Connection Manager — zarzadzanie polaczeniami real-time.

Funkcje:
1. Utrzymuje liste aktywnych polaczen per user per organization
2. Wysyla wiadomosci do konkretnego usera
3. Broadcast do wszystkich userow w organizacji
4. Automatyczny cleanup disconnected clients

Architektura:
  Browser <-> WebSocket <-> ConnectionManager <-> NotificationService
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Zarzadza polaczeniami WebSocket.

    Struktura:
    _connections = {
        "org-uuid-1": {
            "user-uuid-1": {websocket1, websocket2},  # User moze miec wiele tabow
            "user-uuid-2": {websocket3},
        },
    }

    _user_connections = {
        "user-uuid-1": {websocket1, websocket2},  # Quick lookup per user (across orgs)
    }
    """

    def __init__(self):
        # org_id -> user_id -> set of websockets
        self._connections: Dict[str, Dict[str, Set[WebSocket]]] = {}
        # user_id -> set of websockets (flat, across orgs)
        self._user_connections: Dict[str, Set[WebSocket]] = {}
        # websocket -> metadata
        self._metadata: Dict[WebSocket, dict] = {}

    # === CONNECT / DISCONNECT ===

    async def connect(
        self,
        websocket: WebSocket,
        user_id: str,
        organization_id: Optional[str] = None,
    ) -> None:
        """Akceptuj nowe polaczenie WebSocket."""
        await websocket.accept()

        # Zapisz w strukturze org -> user -> websockets
        if organization_id:
            if organization_id not in self._connections:
                self._connections[organization_id] = {}
            if user_id not in self._connections[organization_id]:
                self._connections[organization_id][user_id] = set()
            self._connections[organization_id][user_id].add(websocket)

        # Zapisz w flat user lookup
        if user_id not in self._user_connections:
            self._user_connections[user_id] = set()
        self._user_connections[user_id].add(websocket)

        # Metadata
        self._metadata[websocket] = {
            "user_id": user_id,
            "organization_id": organization_id,
            "connected_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"WebSocket connected: user={user_id}, org={organization_id}")

    async def disconnect(self, websocket: WebSocket) -> None:
        """Zamknij polaczenie i wyczysc ze struktur."""
        meta = self._metadata.pop(websocket, {})
        user_id = meta.get("user_id")
        org_id = meta.get("organization_id")

        # Usun z org -> user -> websockets
        if org_id and org_id in self._connections:
            if user_id and user_id in self._connections[org_id]:
                self._connections[org_id][user_id].discard(websocket)
                if not self._connections[org_id][user_id]:
                    del self._connections[org_id][user_id]
            if not self._connections[org_id]:
                del self._connections[org_id]

        # Usun z flat user lookup
        if user_id and user_id in self._user_connections:
            self._user_connections[user_id].discard(websocket)
            if not self._user_connections[user_id]:
                del self._user_connections[user_id]

        logger.info(f"WebSocket disconnected: user={user_id}")

    # === WYSYLANIE ===

    async def send_to_user(self, user_id: str, message: dict) -> int:
        """
        Wyslij wiadomosc do WSZYSTKICH polaczen danego usera.
        Zwraca liczbe polaczen do ktorych wyslano.
        """
        connections = self._user_connections.get(user_id, set())
        sent = 0
        dead = []

        for ws in connections:
            try:
                await ws.send_json(message)
                sent += 1
            except Exception:
                dead.append(ws)

        # Cleanup dead connections
        for ws in dead:
            await self.disconnect(ws)

        return sent

    async def broadcast_to_organization(
        self, organization_id: str, message: dict, exclude_user: Optional[str] = None
    ) -> int:
        """
        Broadcast do wszystkich userow w organizacji.
        exclude_user: pomin tego usera (np. autora zmiany)
        """
        org_connections = self._connections.get(organization_id, {})
        sent = 0

        for uid, websockets in list(org_connections.items()):
            if exclude_user and uid == exclude_user:
                continue
            for ws in list(websockets):
                try:
                    await ws.send_json(message)
                    sent += 1
                except Exception:
                    await self.disconnect(ws)

        return sent

    async def broadcast_all(self, message: dict) -> int:
        """Broadcast do WSZYSTKICH polaczonych userow (np. maintenance notice)."""
        sent = 0
        for uid, websockets in list(self._user_connections.items()):
            for ws in list(websockets):
                try:
                    await ws.send_json(message)
                    sent += 1
                except Exception:
                    await self.disconnect(ws)
        return sent

    # === STATUS ===

    def is_user_online(self, user_id: str) -> bool:
        """Sprawdz czy user jest online (ma aktywne polaczenie)."""
        return user_id in self._user_connections and len(self._user_connections[user_id]) > 0

    def get_online_users(self, organization_id: Optional[str] = None) -> list:
        """Lista online userow (opcjonalnie w organizacji)."""
        if organization_id:
            org_connections = self._connections.get(organization_id, {})
            return list(org_connections.keys())
        return list(self._user_connections.keys())

    def get_connection_count(self) -> dict:
        """Statystyki polaczen."""
        total_connections = sum(
            len(ws_set) for ws_set in self._user_connections.values()
        )
        return {
            "total_connections": total_connections,
            "online_users": len(self._user_connections),
            "organizations": len(self._connections),
        }


# === SINGLETON ===
_manager_instance: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """Zwraca globalna instancje ConnectionManager."""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = ConnectionManager()
    return _manager_instance
