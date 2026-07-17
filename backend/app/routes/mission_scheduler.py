from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.mission_task_scheduler import (
    get_mission_task_summary,
    get_next_ready_task,
    get_ready_tasks,
)


router = APIRouter(
    prefix="/mission-scheduler",
    tags=["Mission Scheduler"],
)


@router.get("/{mission_id}/summary")
def scheduler_summary(
    mission_id: str,
    db: Session = Depends(get_db),
):
    return get_mission_task_summary(
        db,
        mission_id,
    )


@router.get("/{mission_id}/next")
def next_task(
    mission_id: str,
    db: Session = Depends(get_db),
):
    task = get_next_ready_task(
        db,
        mission_id,
    )

    if task is None:
        return {
            "next_task": None,
        }

    return {
        "task_uid": task.task_uid,
        "agent_name": task.agent_name,
        "task_type": task.task_type,
        "title": task.title,
        "status": task.status,
        "sequence_number": task.sequence_number,
    }


@router.get("/{mission_id}/ready")
def ready_tasks(
    mission_id: str,
    db: Session = Depends(get_db),
):
    tasks = get_ready_tasks(
        db,
        mission_id,
    )

    return [
        {
            "task_uid": task.task_uid,
            "agent_name": task.agent_name,
            "task_type": task.task_type,
            "title": task.title,
            "status": task.status,
            "sequence_number": task.sequence_number,
        }
        for task in tasks
    ]