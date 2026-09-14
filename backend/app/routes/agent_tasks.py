from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.business.access import get_current_business_uid
from app.database.database import get_db
from app.database.models import AgentTask, Mission
from app.schemas.agent_task import (
    AgentTaskCreate,
    AgentTaskResponse,
    AgentTaskUpdate,
)
from app.services.agent_task_service import (
    cancel_agent_task,
    complete_agent_task,
    create_agent_task,
    delete_agent_task,
    get_agent_task,
    get_mission_tasks,
    get_next_runnable_task,
    list_agent_tasks,
    retry_agent_task,
    start_agent_task,
    update_agent_task,
    update_task_progress,
)


router = APIRouter(
    prefix="/agent-tasks",
    tags=["Agent Tasks"],
)


def require_workspace_mission(
    mission_id: str,
    business_uid: str,
    db: Session,
) -> Mission:
    mission = (
        db.query(Mission)
        .filter(
            Mission.mission_uid == mission_id,
            Mission.business_uid == business_uid,
        )
        .first()
    )

    if mission is None:
        raise HTTPException(
            status_code=404,
            detail="Persisted mission not found.",
        )

    return mission


def require_workspace_task(
    task_uid: str,
    business_uid: str,
    db: Session,
) -> AgentTask:
    task = get_agent_task(db, task_uid)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Agent task not found",
        )

    require_workspace_mission(
        task.mission_id,
        business_uid,
        db,
    )

    return task


@router.post(
    "",
    response_model=AgentTaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task_data: AgentTaskCreate,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid,
    ),
):
    require_workspace_mission(
        task_data.mission_id,
        business_uid,
        db,
    )

    return create_agent_task(db, task_data)


@router.get(
    "",
    response_model=list[AgentTaskResponse],
)
def list_tasks(
    mission_id: Optional[str] = None,
    agent_name: Optional[str] = None,
    status_filter: Optional[str] = Query(
        default=None,
        alias="status",
    ),
    priority: Optional[str] = None,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid,
    ),
):
    if mission_id:
        require_workspace_mission(
            mission_id,
            business_uid,
            db,
        )

    return list_agent_tasks(
        db,
        mission_id=mission_id,
        agent_name=agent_name,
        status=status_filter,
        priority=priority,
        business_uid=business_uid,
    )


@router.get(
    "/missions/{mission_id}",
    response_model=list[AgentTaskResponse],
)
def mission_tasks(
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

    return get_mission_tasks(db, mission_id)


@router.get(
    "/missions/{mission_id}/next",
    response_model=Optional[AgentTaskResponse],
)
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

    return get_next_runnable_task(
        db,
        mission_id,
    )


@router.get(
    "/{task_uid}",
    response_model=AgentTaskResponse,
)
def get_task(
    task_uid: str,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid,
    ),
):
    return require_workspace_task(
        task_uid,
        business_uid,
        db,
    )


@router.patch(
    "/{task_uid}",
    response_model=AgentTaskResponse,
)
def update_task(
    task_uid: str,
    update_data: AgentTaskUpdate,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid,
    ),
):
    task = require_workspace_task(
        task_uid,
        business_uid,
        db,
    )
    return update_agent_task(
        db,
        task,
        update_data,
    )


@router.post(
    "/{task_uid}/start",
    response_model=AgentTaskResponse,
)
def start_task(
    task_uid: str,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid,
    ),
):
    task = require_workspace_task(
        task_uid,
        business_uid,
        db,
    )
    return start_agent_task(db, task)


@router.patch(
    "/{task_uid}/progress/{progress}",
    response_model=AgentTaskResponse,
)
def progress(
    task_uid: str,
    progress: int,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid,
    ),
):
    task = require_workspace_task(
        task_uid,
        business_uid,
        db,
    )
    return update_task_progress(
        db,
        task,
        progress,
    )


@router.post(
    "/{task_uid}/complete",
    response_model=AgentTaskResponse,
)
def complete(
    task_uid: str,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid,
    ),
):
    task = require_workspace_task(
        task_uid,
        business_uid,
        db,
    )
    return complete_agent_task(db, task)


@router.post(
    "/{task_uid}/retry",
    response_model=AgentTaskResponse,
)
def retry(
    task_uid: str,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid,
    ),
):
    task = require_workspace_task(
        task_uid,
        business_uid,
        db,
    )
    return retry_agent_task(db, task)


@router.post(
    "/{task_uid}/cancel",
    response_model=AgentTaskResponse,
)
def cancel(
    task_uid: str,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid,
    ),
):
    task = require_workspace_task(
        task_uid,
        business_uid,
        db,
    )
    return cancel_agent_task(db, task)


@router.delete(
    "/{task_uid}",
    status_code=204,
)
def delete(
    task_uid: str,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid,
    ),
):
    task = require_workspace_task(
        task_uid,
        business_uid,
        db,
    )
    delete_agent_task(db, task)
