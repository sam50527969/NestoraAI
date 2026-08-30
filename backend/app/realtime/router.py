from __future__ import annotations

import asyncio
import json

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from pydantic import (
    BaseModel,
    Field,
)
from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_user,
)
from app.auth.security import (
    decode_access_token,
)
from app.auth.service import (
    get_user_by_uid,
)
from app.business.access import (
    get_current_business_uid,
    resolve_business_membership,
)
from app.database.database import (
    get_db,
)
from app.realtime.connection_manager import (
    connection_manager,
)
from app.realtime.events import (
    build_event,
)
from app.realtime.mission_event_publisher import (
    mission_event_publisher,
)
from app.realtime.workforce_registry import (
    workforce_registry,
)


router = APIRouter(
    prefix="/realtime",
    tags=["Realtime"],
)

AUTHENTICATION_TIMEOUT_SECONDS = 10
UNAUTHORIZED_WEBSOCKET_CODE = 4401


class WorkforceUpdateRequest(
    BaseModel
):
    executive: str
    status: str | None = None
    task: str | None = None

    progress: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )


async def authenticate_websocket(
    websocket: WebSocket,
    db: Session,
) -> tuple[str, str] | None:
    await connection_manager.accept(
        websocket
    )

    try:
        raw_message = await asyncio.wait_for(
            websocket.receive_text(),
            timeout=(
                AUTHENTICATION_TIMEOUT_SECONDS
            ),
        )

        payload = json.loads(
            raw_message
        )
    except (
        TimeoutError,
        json.JSONDecodeError,
        WebSocketDisconnect,
    ):
        await websocket.close(
            code=(
                UNAUTHORIZED_WEBSOCKET_CODE
            ),
        )

        return None

    if not isinstance(payload, dict):
        await websocket.close(
            code=(
                UNAUTHORIZED_WEBSOCKET_CODE
            ),
        )

        return None

    if (
        payload.get("event")
        != "socket.authenticate"
    ):
        await websocket.close(
            code=(
                UNAUTHORIZED_WEBSOCKET_CODE
            ),
        )

        return None

    token = payload.get("token")

    if not isinstance(token, str):
        await websocket.close(
            code=(
                UNAUTHORIZED_WEBSOCKET_CODE
            ),
        )

        return None

    user_uid = decode_access_token(
        token
    )

    if user_uid is None:
        await websocket.close(
            code=(
                UNAUTHORIZED_WEBSOCKET_CODE
            ),
        )

        return None

    user = get_user_by_uid(
        db,
        user_uid,
    )

    if (
        user is None
        or not user.is_active
    ):
        await websocket.close(
            code=(
                UNAUTHORIZED_WEBSOCKET_CODE
            ),
        )

        return None

    selected_business_uid = payload.get(
        "business_uid"
    )

    if (
        selected_business_uid is not None
        and not isinstance(selected_business_uid, str)
    ):
        await websocket.close(code=UNAUTHORIZED_WEBSOCKET_CODE)
        return None

    try:
        membership = resolve_business_membership(
            db,
            user_uid=user.user_uid,
            selected_business_uid=selected_business_uid,
        )
    except HTTPException:
        await websocket.close(code=UNAUTHORIZED_WEBSOCKET_CODE)
        return None

    business_uid = membership.business_uid

    connection_manager.register(
        websocket,
        business_uid,
    )

    await (
        connection_manager
        .send_personal_message(
            build_event(
                "socket.authenticated",
                {
                    "user_uid":
                        user.user_uid,
                    "business_uid":
                        business_uid,
                },
            ),
            websocket,
        )
    )

    return user.user_uid, business_uid


@router.websocket("/workforce")
async def workforce_websocket(
    websocket: WebSocket,
    db: Session = Depends(get_db),
) -> None:
    mission_event_publisher.register_current_loop()

    authenticated_context = (
        await authenticate_websocket(
            websocket,
            db,
        )
    )

    if authenticated_context is None:
        return

    _, business_uid = authenticated_context

    try:
        await (
            connection_manager
            .send_personal_message(
                build_event(
                    "workforce.snapshot",
                    workforce_registry
                    .get_all(business_uid),
                ),
                websocket,
            )
        )

        while True:
            message = (
                await websocket
                .receive_text()
            )

            if (
                message
                .strip()
                .lower()
                == "ping"
            ):
                await (
                    connection_manager
                    .send_personal_message(
                        build_event(
                            "pong",
                            {},
                        ),
                        websocket,
                    )
                )

    except WebSocketDisconnect:
        connection_manager.disconnect(
            websocket
        )

    except Exception:
        connection_manager.disconnect(
            websocket
        )
        raise


@router.get(
    "/workforce",
    dependencies=[
        Depends(
            get_current_user,
        ),
    ],
)
def get_workforce(
    business_uid: str = Depends(
        get_current_business_uid,
    ),
) -> dict:
    return {
        "executives":
            workforce_registry.get_all(business_uid),
    }


@router.post(
    "/workforce/update",
    dependencies=[
        Depends(
            get_current_user,
        ),
    ],
)
async def update_workforce(
    payload: WorkforceUpdateRequest,
    business_uid: str = Depends(
        get_current_business_uid,
    ),
) -> dict:
    mission_event_publisher.register_current_loop()

    if (
        not workforce_registry.has_executive(
            business_uid,
            payload.executive,
        )
    ):
        raise HTTPException(
            status_code=404,
            detail=(
                "Executive not found"
            ),
        )

    workforce_registry.update(
        business_uid,
        payload.executive,
        status=payload.status,
        task=payload.task,
        progress=payload.progress,
    )

    executive_data = workforce_registry.get(
        business_uid,
        payload.executive,
    )

    event = build_event(
        "workforce.updated",
        executive_data,
    )

    await connection_manager.broadcast(
        event,
        business_uid,
    )

    return {
        "message": (
            "Workforce status updated"
        ),
        "event": event,
    }
