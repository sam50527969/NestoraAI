import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.database.models import AgentTask


class AgentTaskRepository:
    """
    Repository responsible for persisting AI executive tasks.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        *,
        mission_id: str,
        executive: str,
        title: str,
        description: str,
        priority: str = "medium",
        sequence_number: int = 0,
        depends_on: str | None = None,
        estimated_value: float | None = None,
        input_data: dict[str, Any] | None = None,
    ) -> AgentTask:
        task = AgentTask(
            mission_id=mission_id,
            agent_name=executive,
            task_type="mission",
            title=title,
            description=description,
            priority=priority,
            sequence_number=sequence_number,
            depends_on_task_uid=depends_on,
            estimated_value=estimated_value,
            input_data=self._serialize(input_data),
            status="pending",
            progress=0,
        )

        self._db.add(task)
        self._db.commit()
        self._db.refresh(task)

        return task

    def get_by_uid(
        self,
        task_uid: str,
    ) -> AgentTask | None:
        return (
            self._db.query(AgentTask)
            .filter(AgentTask.task_uid == task_uid)
            .first()
        )

    def list_by_mission(
        self,
        mission_id: str,
    ) -> list[AgentTask]:
        return (
            self._db.query(AgentTask)
            .filter(AgentTask.mission_id == mission_id)
            .order_by(
                AgentTask.sequence_number.asc(),
                AgentTask.created_at.asc(),
            )
            .all()
        )

    def list_pending_by_mission(
        self,
        mission_id: str,
    ) -> list[AgentTask]:
        return (
            self._db.query(AgentTask)
            .filter(
                AgentTask.mission_id == mission_id,
                AgentTask.status == "pending",
            )
            .order_by(
                AgentTask.sequence_number.asc(),
                AgentTask.created_at.asc(),
            )
            .all()
        )

    def update_status(
        self,
        task_uid: str,
        status: str,
    ) -> AgentTask | None:
        task = self.get_by_uid(task_uid)

        if task is None:
            return None

        task.status = status

        self._db.commit()
        self._db.refresh(task)

        return task

    def update_progress(
        self,
        task_uid: str,
        progress: int,
    ) -> AgentTask | None:
        task = self.get_by_uid(task_uid)

        if task is None:
            return None

        task.progress = max(0, min(progress, 100))

        self._db.commit()
        self._db.refresh(task)

        return task

    def mark_running(
        self,
        task_uid: str,
    ) -> AgentTask | None:
        task = self.get_by_uid(task_uid)

        if task is None:
            return None

        task.status = "running"
        task.progress = 10
        task.started_at = task.started_at or datetime.utcnow()
        task.completed_at = None
        task.error_message = None

        self._db.commit()
        self._db.refresh(task)

        return task

    def mark_completed(
        self,
        task_uid: str,
        output_data: dict[str, Any],
    ) -> AgentTask | None:
        task = self.get_by_uid(task_uid)

        if task is None:
            return None

        task.status = "completed"
        task.progress = 100
        task.output_data = self._serialize(output_data)
        task.error_message = None
        task.completed_at = datetime.utcnow()

        self._db.commit()
        self._db.refresh(task)

        return task

    def mark_failed(
        self,
        task_uid: str,
        error_message: str,
    ) -> AgentTask | None:
        task = self.get_by_uid(task_uid)

        if task is None:
            return None

        task.status = "failed"
        task.error_message = error_message
        task.completed_at = datetime.utcnow()

        self._db.commit()
        self._db.refresh(task)

        return task

    def reset_for_retry(
        self,
        task_uid: str,
    ) -> AgentTask | None:
        task = self.get_by_uid(task_uid)

        if task is None:
            return None

        task.retry_count += 1
        task.status = "pending"
        task.progress = 0
        task.error_message = None
        task.started_at = None
        task.completed_at = None

        self._db.commit()
        self._db.refresh(task)

        return task

    @staticmethod
    def deserialize_input(
        task: AgentTask,
    ) -> dict[str, Any]:
        return AgentTaskRepository._deserialize(task.input_data)

    @staticmethod
    def deserialize_output(
        task: AgentTask,
    ) -> dict[str, Any]:
        return AgentTaskRepository._deserialize(task.output_data)

    @staticmethod
    def _serialize(
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
    def _deserialize(
        value: str | None,
    ) -> dict[str, Any]:
        if not value:
            return {}

        try:
            parsed = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return {}

        if not isinstance(parsed, dict):
            return {}

        return parsed