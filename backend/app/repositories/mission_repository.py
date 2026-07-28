import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.database.models import Mission


class MissionRepository:
    """
    Persistence layer for Mission records.

    This repository is responsible only for database access.
    Mission planning and task-generation logic should remain
    in dedicated services.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        *,
        business_uid: str,
        title: str,
        objective: str,
        description: str | None = None,
        objective_uid: str | None = None,
        status: str = "planned",
        priority: str = "medium",
        estimated_value: float | None = None,
        expected_roi: float | None = None,
        strategy_data: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Mission:
        mission = Mission(
            business_uid=business_uid,
            objective_uid=objective_uid,
            title=title,
            objective=objective,
            description=description,
            status=status,
            priority=priority,
            estimated_value=estimated_value,
            expected_roi=expected_roi,
            progress=0,
            strategy_data=self._serialize_json(strategy_data),
            metadata_json=self._serialize_json(metadata),
        )

        self._db.add(mission)
        self._db.commit()
        self._db.refresh(mission)

        return mission

    def get_by_uid(
        self,
        mission_uid: str,
    ) -> Mission | None:
        return (
            self._db.query(Mission)
            .filter(Mission.mission_uid == mission_uid)
            .first()
        )

    def list_by_business(
        self,
        business_uid: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Mission]:
        return (
            self._db.query(Mission)
            .filter(Mission.business_uid == business_uid)
            .order_by(Mission.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def list_all(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Mission]:
        return (
            self._db.query(Mission)
            .order_by(Mission.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def update_status(
        self,
        mission_uid: str,
        status: str,
    ) -> Mission | None:
        mission = self.get_by_uid(mission_uid)

        if mission is None:
            return None

        mission.status = status

        self._db.commit()
        self._db.refresh(mission)

        return mission

    def update_progress(
        self,
        mission_uid: str,
        progress: int,
    ) -> Mission | None:
        mission = self.get_by_uid(mission_uid)

        if mission is None:
            return None

        mission.progress = max(0, min(progress, 100))

        self._db.commit()
        self._db.refresh(mission)

        return mission

    def mark_running(
        self,
        mission_uid: str,
    ) -> Mission | None:
        mission = self.get_by_uid(mission_uid)

        if mission is None:
            return None

        mission.status = "running"
        mission.started_at = mission.started_at or datetime.utcnow()
        mission.completed_at = None

        self._db.commit()
        self._db.refresh(mission)

        return mission

    def mark_completed(
        self,
        mission_uid: str,
    ) -> Mission | None:
        mission = self.get_by_uid(mission_uid)

        if mission is None:
            return None

        mission.status = "completed"
        mission.progress = 100
        mission.completed_at = datetime.utcnow()

        self._db.commit()
        self._db.refresh(mission)

        return mission

    def mark_failed(
        self,
        mission_uid: str,
    ) -> Mission | None:
        mission = self.get_by_uid(mission_uid)

        if mission is None:
            return None

        mission.status = "failed"
        mission.completed_at = datetime.utcnow()

        self._db.commit()
        self._db.refresh(mission)

        return mission

    def delete(
        self,
        mission_uid: str,
    ) -> bool:
        mission = self.get_by_uid(mission_uid)

        if mission is None:
            return False

        self._db.delete(mission)
        self._db.commit()

        return True

    @staticmethod
    def deserialize_strategy(
        mission: Mission,
    ) -> dict[str, Any] | None:
        return MissionRepository._deserialize_json(
            mission.strategy_data
        )

    @staticmethod
    def deserialize_metadata(
        mission: Mission,
    ) -> dict[str, Any] | None:
        return MissionRepository._deserialize_json(
            mission.metadata_json
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