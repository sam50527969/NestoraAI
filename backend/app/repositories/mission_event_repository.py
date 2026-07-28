import json
from typing import Any

from sqlalchemy.orm import Session

from app.database.models import MissionEvent


class MissionEventRepository:
    """
    Persistence layer for MissionEvent records.

    Mission events are immutable execution-history records.
    New events should be appended rather than updated.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def create_event(
        self,
        *,
        mission_uid: str,
        executive: str,
        event_type: str,
        message: str,
        status: str = "info",
        metadata: dict[str, Any] | None = None,
    ) -> MissionEvent:
        event = MissionEvent(
            mission_uid=mission_uid,
            executive=executive,
            event_type=event_type,
            status=status,
            message=message,
            metadata_json=self._serialize_json(metadata),
        )

        self._db.add(event)
        self._db.commit()
        self._db.refresh(event)

        return event

    def get_by_uid(
        self,
        event_uid: str,
    ) -> MissionEvent | None:
        return (
            self._db.query(MissionEvent)
            .filter(MissionEvent.event_uid == event_uid)
            .first()
        )

    def list_by_mission(
        self,
        mission_uid: str,
        *,
        limit: int = 200,
        offset: int = 0,
    ) -> list[MissionEvent]:
        return (
            self._db.query(MissionEvent)
            .filter(MissionEvent.mission_uid == mission_uid)
            .order_by(MissionEvent.created_at.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def list_by_executive(
        self,
        executive: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MissionEvent]:
        return (
            self._db.query(MissionEvent)
            .filter(MissionEvent.executive == executive)
            .order_by(MissionEvent.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def list_by_status(
        self,
        status: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MissionEvent]:
        return (
            self._db.query(MissionEvent)
            .filter(MissionEvent.status == status)
            .order_by(MissionEvent.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def latest_event(
        self,
        mission_uid: str,
    ) -> MissionEvent | None:
        return (
            self._db.query(MissionEvent)
            .filter(MissionEvent.mission_uid == mission_uid)
            .order_by(MissionEvent.created_at.desc())
            .first()
        )

    def latest_by_executive(
        self,
        mission_uid: str,
        executive: str,
    ) -> MissionEvent | None:
        return (
            self._db.query(MissionEvent)
            .filter(
                MissionEvent.mission_uid == mission_uid,
                MissionEvent.executive == executive,
            )
            .order_by(MissionEvent.created_at.desc())
            .first()
        )

    def count_by_mission(
        self,
        mission_uid: str,
    ) -> int:
        return (
            self._db.query(MissionEvent)
            .filter(MissionEvent.mission_uid == mission_uid)
            .count()
        )

    @staticmethod
    def deserialize_metadata(
        event: MissionEvent,
    ) -> dict[str, Any] | None:
        return MissionEventRepository._deserialize_json(
            event.metadata_json
        )

    @staticmethod
    def _serialize_json(
        value: dict[str, Any] | None,
    ) -> str | None:
        if value is None:
            return None

        return json.dumps(
            value,
            ensure_ascii=False,
            default=str,
        )

    @staticmethod
    def _deserialize_json(
        value: str | None,
    ) -> dict[str, Any] | None:
        if not value:
            return None

        try:
            parsed = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return None

        if not isinstance(parsed, dict):
            return None

        return parsed