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

    async def accept(
        self,
        websocket: WebSocket,
    ) -> None:
        await websocket.accept()

    def register(
        self,
        websocket: WebSocket,
    ) -> None:
        if (
            websocket
            not in self.active_connections
        ):
            self.active_connections.append(
                websocket
            )

    async def connect(
        self,
        websocket: WebSocket,
    ) -> None:
        await self.accept(websocket)
        self.register(websocket)

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
    ) -> None:
        disconnected_connections: list[
            WebSocket
        ] = []

        for connection in (
            self.active_connections
        ):
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