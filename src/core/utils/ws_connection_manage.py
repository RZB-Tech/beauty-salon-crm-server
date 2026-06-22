from __future__ import annotations
from typing import TYPE_CHECKING
from fastapi import WebSocket
from collections import defaultdict

if TYPE_CHECKING:
    from src.repository.notification.notification_model import Notification

class ConnectionManager:
    def __init__(self):
        self._connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, websocket: WebSocket, agent_id: int) -> None:
        await websocket.accept()
        self._connections[agent_id].add(websocket)

    def disconnect(self, websocket: WebSocket, agent_id: int) -> None:
        self._connections[agent_id].discard(websocket)
        if not self._connections[agent_id]:
            del self._connections[agent_id]

    async def send(self, notification: "Notification", agent_id: int) -> bool:
        """
        Push to all sockets of the agent who owns this client.
        Returns True if agent was online.
        """
        sockets = self._connections.get(agent_id)
        if not sockets:
            return False

        payload = _serialize(notification)
        dead: set[WebSocket] = set()

        for ws in sockets:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.add(ws)

        for ws in dead:
            self.disconnect(ws, agent_id)

        return len(dead) < len(sockets)  # True if at least one delivery succeeded

    @property
    def online_agents(self) -> set[int]:
        return set(self._connections.keys())


def _serialize(notification: "Notification") -> dict:
    return {
        "id":           notification.id,
        "client_id":    notification.client_id,
        "type":         notification.type.value,
        "title":        notification.title,
        "body":         notification.body,
        "scheduled_at": notification.scheduled_at.isoformat(),
        "delivered_at": notification.delivered_at.isoformat() if notification.delivered_at else None,
    }


manager = ConnectionManager()