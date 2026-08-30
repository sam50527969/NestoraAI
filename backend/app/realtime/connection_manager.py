from __future__ import annotations

from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    """
    Manage authenticated realtime
    WebSocket connections.
    """

    def __init__(self) -> None:
        self.active_connections: list[
            WebSocket
        ] = []
        self._business_by_connection: dict[WebSocket, str] = {}

    async def accept(
        self,
        websocket: WebSocket,
    ) -> None:
        await websocket.accept()

    def register(
        self,
        websocket: WebSocket,
        business_uid: str,
    ) -> None:
        if (
            websocket
            not in self.active_connections
        ):
            self.active_connections.append(
                websocket
            )

        self._business_by_connection[websocket] = business_uid

    async def connect(
        self,
        websocket: WebSocket,
        business_uid: str,
    ) -> None:
        await self.accept(websocket)
        self.register(websocket, business_uid)

    def disconnect(
        self,
        websocket: WebSocket,
    ) -> None:
        if (
            websocket
            in self.active_connections
        ):
            self.active_connections.remove(
                websocket
            )

        self._business_by_connection.pop(websocket, None)

    def clear(self) -> None:
        self.active_connections.clear()
        self._business_by_connection.clear()

    async def send_personal_message(
        self,
        message: dict[str, Any],
        websocket: WebSocket,
    ) -> None:
        await websocket.send_json(
            message
        )

    async def broadcast(
        self,
        message: dict[str, Any],
        business_uid: str,
    ) -> None:
        disconnected_connections: list[
            WebSocket
        ] = []

        for connection in (
            self.active_connections
        ):
            if (
                self._business_by_connection.get(connection)
                != business_uid
            ):
                continue

            try:
                await connection.send_json(
                    message
                )
            except Exception:
                disconnected_connections.append(
                    connection
                )

        for connection in (
            disconnected_connections
        ):
            self.disconnect(connection)


connection_manager = (
    ConnectionManager()
)
