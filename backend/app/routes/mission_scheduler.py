from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.business.access import get_current_business_uid
from app.database.database import get_db
from app.repositories.mission_repository import MissionRepository
from app.services.mission_task_scheduler import (
    get_mission_task_summary,
    get_next_ready_task,
    get_ready_tasks,
)


router = APIRouter(
    prefix="/mission-scheduler",
    tags=["Mission Scheduler"],
)


def require_workspace_mission(
    mission_id: str,
    business_uid: str,
    db: Session,
):
    mission = MissionRepository(
        db
    ).get_by_uid_and_business(
        mission_id,
        business_uid,
    )

    if mission is None:
        raise HTTPException(
            status_code=404,
            detail="Persisted mission not found.",
        )

    return mission


@router.get("/{mission_id}/summary")
def scheduler_summary(
    mission_id: str,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid,
    ),
):
    require_workspace_mission(
        mission_id,
        business_uid,
        db,
    )

    return get_mission_task_summary(
        db,
        mission_id,
    )


@router.get("/{mission_id}/next")
def next_task(
    mission_id: str,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid,
    ),
):
    require_workspace_mission(
        mission_id,
        business_uid,
        db,
    )

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
    business_uid: str = Depends(
        get_current_business_uid,
    ),
):
    require_workspace_mission(
        mission_id,
        business_uid,
        db,
    )

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
