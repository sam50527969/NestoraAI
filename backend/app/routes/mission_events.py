from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
)
from sqlalchemy.orm import Session

from app.database.database import (
    get_db,
)
from app.repositories.mission_event_repository import (
    MissionEventRepository,
)
from app.repositories.mission_repository import (
    MissionRepository,
)
from app.schemas.mission_event import (
    MissionEventListResponse,
    MissionEventResponse,
)


router = APIRouter(
    prefix="/missions",
    tags=["Mission Timeline"],
)


@router.get(
    "/{mission_uid}/events",
    response_model=(
        MissionEventListResponse
    ),
)
def get_mission_events(
    mission_uid: str = Path(
        min_length=1,
        max_length=100,
    ),
    limit: int = Query(
        default=200,
        ge=1,
        le=500,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    db: Session = Depends(get_db),
) -> MissionEventListResponse:
    mission_repository = (
        MissionRepository(db)
    )

    mission = (
        mission_repository.get_by_uid(
            mission_uid
        )
    )

    if mission is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Persisted mission not found."
            ),
        )

    event_repository = (
        MissionEventRepository(db)
    )

    events = (
        event_repository.list_by_mission(
            mission_uid,
            limit=limit,
            offset=offset,
        )
    )

    return MissionEventListResponse(
        mission_uid=mission_uid,
        count=len(events),
        events=[
            MissionEventResponse(
                event_uid=event.event_uid,
                executive=event.executive,
                event_type=(
                    event.event_type
                ),
                status=event.status,
                message=event.message,
                metadata=(
                    event_repository
                    .deserialize_metadata(
                        event
                    )
                ),
                created_at=(
                    event.created_at
                ),
            )
            for event in events
        ],
    )