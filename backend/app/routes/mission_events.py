from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.repositories.mission_event_repository import (
    MissionEventRepository,
)

router = APIRouter(
    prefix="/missions",
    tags=["Mission Timeline"],
)


@router.get("/{mission_uid}/events")
def get_mission_events(
    mission_uid: str,
    db: Session = Depends(get_db),
):
    """
    Return every execution event belonging to one mission.
    """

    repository = MissionEventRepository(db)

    events = repository.list_by_mission(
        mission_uid
    )

    if not events:
        raise HTTPException(
            status_code=404,
            detail="No mission events found.",
        )

    return {
        "mission_uid": mission_uid,
        "count": len(events),
        "events": [
            {
                "event_uid": event.event_uid,
                "executive": event.executive,
                "event_type": event.event_type,
                "status": event.status,
                "message": event.message,
                "metadata": repository.deserialize_metadata(
                    event
                ),
                "created_at": event.created_at,
            }
            for event in events
        ],
    }