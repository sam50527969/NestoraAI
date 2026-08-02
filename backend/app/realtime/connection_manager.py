from __future__ import annotations

from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    """
    Manages active WebSocket connections for Nestora's real-time updates.
    """

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(
        self,
        message: dict[str, Any],
        websocket: WebSocket,
    ) -> None:
        await websocket.send_json(message)

    async def broadcast(
        self,
        message: dict[str, Any],
    ) -> None:
        print(
            "BROADCAST CALLED | connections:",
            len(self.active_connections),
        )
        print("BROADCAST MESSAGE:", message)

        disconnected_connections: list[WebSocket] = []

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
                print("BROADCAST SENT SUCCESSFULLY")
            except Exception as exc:
                print(
                    "BROADCAST FAILED:",
                    type(exc).__name__,
                    str(exc),
                )
                disconnected_connections.append(connection)

        for connection in disconnected_connections:
            self.disconnect(connection)


connection_manager = ConnectionManager()