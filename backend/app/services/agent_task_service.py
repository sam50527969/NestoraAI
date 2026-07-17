import json
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.database.models import AgentTask
from app.schemas.agent_task import AgentTaskCreate, AgentTaskUpdate


VALID_STATUSES = {
    "pending",
    "ready",
    "running",
    "completed",
    "failed",
    "cancelled",
}

VALID_PRIORITIES = {
    "low",
    "medium",
    "high",
    "critical",
}


def _serialize_json(value: Any) -> Optional[str]:
    if value is None:
        return None

    if isinstance(value, str):
        return value

    return json.dumps(
        value,
        ensure_ascii=False,
        default=str,
    )


def _normalize_status(status: str) -> str:
    normalized = str(status or "").strip().lower()

    if normalized not in VALID_STATUSES:
        raise ValueError(
            f"Invalid task status: {status}"
        )

    return normalized


def _normalize_priority(priority: str) -> str:
    normalized = str(
        priority or "medium"
    ).strip().lower()

    if normalized not in VALID_PRIORITIES:
        raise ValueError(
            f"Invalid task priority: {priority}"
        )

    return normalized


def _clamp_progress(progress: int) -> int:
    return max(
        0,
        min(int(progress), 100),
    )


def create_agent_task(
    db: Session,
    task_data: AgentTaskCreate,
    *,
    input_data: Any = None,
    estimated_value: Optional[float] = None,
    max_retries: int = 3,
) -> AgentTask:
    task = AgentTask(
        mission_id=task_data.mission_id,
        agent_name=task_data.agent_name,
        task_type=task_data.task_type,
        title=task_data.title,
        description=task_data.description,
        status="pending",
        priority=_normalize_priority(
            task_data.priority
        ),
        progress=0,
        sequence_number=task_data.sequence_number,
        depends_on_task_uid=(
            task_data.depends_on_task_uid
        ),
        input_data=_serialize_json(input_data),
        estimated_value=estimated_value,
        max_retries=max(0, int(max_retries)),
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def get_agent_task(
    db: Session,
    task_uid: str,
) -> Optional[AgentTask]:
    return (
        db.query(AgentTask)
        .filter(AgentTask.task_uid == task_uid)
        .first()
    )


def get_agent_task_by_id(
    db: Session,
    task_id: int,
) -> Optional[AgentTask]:
    return (
        db.query(AgentTask)
        .filter(AgentTask.id == task_id)
        .first()
    )


def list_agent_tasks(
    db: Session,
    *,
    mission_id: Optional[str] = None,
    agent_name: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    query = db.query(AgentTask)

    if mission_id:
        query = query.filter(
            AgentTask.mission_id == mission_id
        )

    if agent_name:
        query = query.filter(
            AgentTask.agent_name == agent_name
        )

    if status:
        query = query.filter(
            AgentTask.status == _normalize_status(status)
        )

    if priority:
        query = query.filter(
            AgentTask.priority == _normalize_priority(priority)
        )

    return (
        query
        .order_by(
            AgentTask.sequence_number.asc(),
            AgentTask.created_at.asc(),
        )
        .offset(max(0, int(offset)))
        .limit(max(1, min(int(limit), 500)))
        .all()
    )


def get_mission_tasks(
    db: Session,
    mission_id: str,
):
    return list_agent_tasks(
        db,
        mission_id=mission_id,
        limit=500,
    )


def update_agent_task(
    db: Session,
    task: AgentTask,
    update_data: AgentTaskUpdate,
) -> AgentTask:
    if update_data.status is not None:
        task.status = _normalize_status(
            update_data.status
        )

    if update_data.progress is not None:
        task.progress = _clamp_progress(
            update_data.progress
        )

    if update_data.output_data is not None:
        task.output_data = _serialize_json(
            update_data.output_data
        )

    if update_data.error_message is not None:
        task.error_message = update_data.error_message

    task.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return task


def start_agent_task(
    db: Session,
    task: AgentTask,
) -> AgentTask:
    if task.status in {
        "completed",
        "cancelled",
    }:
        raise ValueError(
            f"Cannot start task with status '{task.status}'"
        )

    task.status = "running"
    task.progress = max(task.progress or 0, 1)
    task.started_at = datetime.utcnow()
    task.completed_at = None
    task.error_message = None
    task.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return task


def update_task_progress(
    db: Session,
    task: AgentTask,
    progress: int,
) -> AgentTask:
    if task.status in {
        "completed",
        "cancelled",
    }:
        raise ValueError(
            f"Cannot update progress for task with status '{task.status}'"
        )

    task.progress = _clamp_progress(progress)

    if task.status in {
        "pending",
        "ready",
    }:
        task.status = "running"
        task.started_at = (
            task.started_at
            or datetime.utcnow()
        )

    task.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return task


def complete_agent_task(
    db: Session,
    task: AgentTask,
    *,
    output_data: Any = None,
) -> AgentTask:
    if task.status == "cancelled":
        raise ValueError(
            "Cancelled tasks cannot be completed"
        )

    task.status = "completed"
    task.progress = 100
    task.output_data = _serialize_json(
        output_data
    )
    task.error_message = None
    task.completed_at = datetime.utcnow()
    task.started_at = (
        task.started_at
        or task.completed_at
    )
    task.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return task


def fail_agent_task(
    db: Session,
    task: AgentTask,
    error_message: str,
) -> AgentTask:
    if task.status == "completed":
        raise ValueError(
            "Completed tasks cannot be failed"
        )

    task.status = "failed"
    task.error_message = str(error_message)
    task.completed_at = datetime.utcnow()
    task.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return task


def retry_agent_task(
    db: Session,
    task: AgentTask,
) -> AgentTask:
    if task.status != "failed":
        raise ValueError(
            "Only failed tasks can be retried"
        )

    if task.retry_count >= task.max_retries:
        raise ValueError(
            "Maximum retry count reached"
        )

    task.retry_count += 1
    task.status = "pending"
    task.progress = 0
    task.error_message = None
    task.started_at = None
    task.completed_at = None
    task.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return task


def cancel_agent_task(
    db: Session,
    task: AgentTask,
) -> AgentTask:
    if task.status == "completed":
        raise ValueError(
            "Completed tasks cannot be cancelled"
        )

    task.status = "cancelled"
    task.completed_at = datetime.utcnow()
    task.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return task


def delete_agent_task(
    db: Session,
    task: AgentTask,
) -> None:
    db.delete(task)
    db.commit()


def is_task_dependency_complete(
    db: Session,
    task: AgentTask,
) -> bool:
    if not task.depends_on_task_uid:
        return True

    dependency = get_agent_task(
        db,
        task.depends_on_task_uid,
    )

    return bool(
        dependency
        and dependency.status == "completed"
    )


def get_next_runnable_task(
    db: Session,
    mission_id: str,
) -> Optional[AgentTask]:
    tasks = get_mission_tasks(
        db,
        mission_id,
    )

    for task in tasks:
        if task.status not in {
            "pending",
            "ready",
        }:
            continue

        if is_task_dependency_complete(
            db,
            task,
        ):
            return task

    return None