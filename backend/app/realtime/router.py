from __future__ import annotations

from fastapi import (
    APIRouter,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from pydantic import BaseModel, Field

from app.realtime.connection_manager import connection_manager
from app.realtime.events import build_event
from app.realtime.mission_event_publisher import (
    mission_event_publisher,
)
from app.realtime.workforce_registry import workforce_registry


router = APIRouter(
    prefix="/realtime",
    tags=["Realtime"],
)


class WorkforceUpdateRequest(BaseModel):
    executive: str
    status: str | None = None
    task: str | None = None
    progress: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )


@router.websocket("/workforce")
async def workforce_websocket(
    websocket: WebSocket,
) -> None:
    mission_event_publisher.register_current_loop()

    await connection_manager.connect(websocket)

    try:
        await connection_manager.send_personal_message(
            build_event(
                "workforce.snapshot",
                workforce_registry.get_all(),
            ),
            websocket,
        )

        while True:
            message = await websocket.receive_text()

            if message.strip().lower() == "ping":
                await connection_manager.send_personal_message(
                    build_event(
                        "pong",
                        {},
                    ),
                    websocket,
                )

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)

    except Exception:
        connection_manager.disconnect(websocket)
        raise


@router.get("/workforce")
def get_workforce() -> dict:
    return {
        "executives": workforce_registry.get_all(),
    }


@router.post("/workforce/update")
async def update_workforce(
    payload: WorkforceUpdateRequest,
) -> dict:
    mission_event_publisher.register_current_loop()

    if payload.executive not in workforce_registry.executives:
        raise HTTPException(
            status_code=404,
            detail="Executive not found",
        )

    workforce_registry.update(
        payload.executive,
        status=payload.status,
        task=payload.task,
        progress=payload.progress,
    )

    executive_data = workforce_registry.executives[
        payload.executive
    ]

    event = build_event(
        "workforce.updated",
        executive_data,
    )

    await connection_manager.broadcast(event)

    return {
        "message": "Workforce status updated",
        "event": event,
    }