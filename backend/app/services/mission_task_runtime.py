from typing import Optional

from sqlalchemy.orm import Session

from app.database.models import AgentTask
from app.services.agent_task_service import (
    complete_agent_task,
    fail_agent_task,
    start_agent_task,
    update_task_progress,
)


def get_task_by_type(
    db: Session,
    mission_id: str,
    task_type: str,
) -> Optional[AgentTask]:
    return (
        db.query(AgentTask)
        .filter(
            AgentTask.mission_id == mission_id,
            AgentTask.task_type == task_type,
        )
        .order_by(AgentTask.sequence_number.asc())
        .first()
    )


def start_mission_task(
    db: Session,
    mission_id: str,
    task_type: str,
) -> Optional[AgentTask]:
    task = get_task_by_type(
        db,
        mission_id,
        task_type,
    )

    if task is None:
        return None

    if task.status == "running":
        return task

    if task.status == "completed":
        return task

    return start_agent_task(
        db,
        task,
    )


def update_mission_task_progress(
    db: Session,
    mission_id: str,
    task_type: str,
    progress: int,
) -> Optional[AgentTask]:
    task = get_task_by_type(
        db,
        mission_id,
        task_type,
    )

    if task is None:
        return None

    if task.status in {
        "completed",
        "cancelled",
    }:
        return task

    return update_task_progress(
        db,
        task,
        progress,
    )


def complete_mission_task(
    db: Session,
    mission_id: str,
    task_type: str,
    *,
    output_data=None,
) -> Optional[AgentTask]:
    task = get_task_by_type(
        db,
        mission_id,
        task_type,
    )

    if task is None:
        return None

    if task.status == "completed":
        return task

    return complete_agent_task(
        db,
        task,
        output_data=output_data,
    )


def fail_mission_task(
    db: Session,
    mission_id: str,
    task_type: str,
    error_message: str,
) -> Optional[AgentTask]:
    task = get_task_by_type(
        db,
        mission_id,
        task_type,
    )

    if task is None:
        return None

    if task.status == "completed":
        return task

    return fail_agent_task(
        db,
        task,
        error_message,
    )