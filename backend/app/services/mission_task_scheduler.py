from typing import List, Optional

from sqlalchemy.orm import Session

from app.database.models import AgentTask


TERMINAL_STATUSES = {
    "completed",
    "failed",
    "cancelled",
}


def get_mission_tasks(
    db: Session,
    mission_id: str,
) -> List[AgentTask]:
    """
    Return every task belonging to a mission in execution order.
    """
    return (
        db.query(AgentTask)
        .filter(AgentTask.mission_id == mission_id)
        .order_by(
            AgentTask.sequence_number.asc(),
            AgentTask.id.asc(),
        )
        .all()
    )


def get_task_by_uid(
    db: Session,
    task_uid: str,
) -> Optional[AgentTask]:
    """
    Return one persistent task using its public task UID.
    """
    return (
        db.query(AgentTask)
        .filter(AgentTask.task_uid == task_uid)
        .first()
    )


def is_dependency_completed(
    db: Session,
    task: AgentTask,
) -> bool:
    """
    A task without a dependency is immediately eligible.

    A task with a dependency becomes eligible only after the
    dependency has completed successfully.
    """
    if not task.depends_on_task_uid:
        return True

    dependency = get_task_by_uid(
        db,
        task.depends_on_task_uid,
    )

    if dependency is None:
        return False

    return dependency.status == "completed"


def is_task_ready(
    db: Session,
    task: AgentTask,
) -> bool:
    """
    Determine whether a task can begin execution.
    """
    if task.status != "pending":
        return False

    return is_dependency_completed(
        db,
        task,
    )


def get_ready_tasks(
    db: Session,
    mission_id: str,
) -> List[AgentTask]:
    """
    Return all pending tasks whose dependencies are complete.

    The current mission plan is sequential, but this method also
    supports multiple ready tasks later when parallel execution is
    introduced.
    """
    tasks = get_mission_tasks(
        db,
        mission_id,
    )

    return [
        task
        for task in tasks
        if is_task_ready(db, task)
    ]


def get_next_ready_task(
    db: Session,
    mission_id: str,
) -> Optional[AgentTask]:
    """
    Return the first task that is ready to execute.
    """
    ready_tasks = get_ready_tasks(
        db,
        mission_id,
    )

    if not ready_tasks:
        return None

    return ready_tasks[0]


def get_running_tasks(
    db: Session,
    mission_id: str,
) -> List[AgentTask]:
    """
    Return all currently running tasks for a mission.
    """
    return (
        db.query(AgentTask)
        .filter(
            AgentTask.mission_id == mission_id,
            AgentTask.status == "running",
        )
        .order_by(
            AgentTask.sequence_number.asc(),
            AgentTask.id.asc(),
        )
        .all()
    )


def get_failed_tasks(
    db: Session,
    mission_id: str,
) -> List[AgentTask]:
    """
    Return all failed tasks for a mission.
    """
    return (
        db.query(AgentTask)
        .filter(
            AgentTask.mission_id == mission_id,
            AgentTask.status == "failed",
        )
        .order_by(
            AgentTask.sequence_number.asc(),
            AgentTask.id.asc(),
        )
        .all()
    )


def is_mission_task_plan_complete(
    db: Session,
    mission_id: str,
) -> bool:
    """
    Return True when every task has reached a terminal status.
    """
    tasks = get_mission_tasks(
        db,
        mission_id,
    )

    if not tasks:
        return False

    return all(
        task.status in TERMINAL_STATUSES
        for task in tasks
    )


def is_mission_task_plan_successful(
    db: Session,
    mission_id: str,
) -> bool:
    """
    Return True only when every task completed successfully.
    """
    tasks = get_mission_tasks(
        db,
        mission_id,
    )

    if not tasks:
        return False

    return all(
        task.status == "completed"
        for task in tasks
    )


def get_mission_task_summary(
    db: Session,
    mission_id: str,
) -> dict:
    """
    Build a compact scheduler summary for API responses and debugging.
    """
    tasks = get_mission_tasks(
        db,
        mission_id,
    )

    counts = {
        "total": len(tasks),
        "pending": 0,
        "running": 0,
        "completed": 0,
        "failed": 0,
        "cancelled": 0,
    }

    for task in tasks:
        if task.status in counts:
            counts[task.status] += 1

    next_task = get_next_ready_task(
        db,
        mission_id,
    )

    running_tasks = get_running_tasks(
        db,
        mission_id,
    )

    return {
        "mission_id": mission_id,
        "counts": counts,
        "is_complete": is_mission_task_plan_complete(
            db,
            mission_id,
        ),
        "is_successful": is_mission_task_plan_successful(
            db,
            mission_id,
        ),
        "next_ready_task": (
            {
                "task_uid": next_task.task_uid,
                "agent_name": next_task.agent_name,
                "task_type": next_task.task_type,
                "title": next_task.title,
                "sequence_number": next_task.sequence_number,
            }
            if next_task
            else None
        ),
        "running_tasks": [
            {
                "task_uid": task.task_uid,
                "agent_name": task.agent_name,
                "task_type": task.task_type,
                "title": task.title,
                "progress": task.progress,
            }
            for task in running_tasks
        ],
    }