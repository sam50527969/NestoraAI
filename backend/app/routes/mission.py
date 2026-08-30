import asyncio
import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.business.access import get_current_business_uid
from app.database.database import get_db
from app.repositories.agent_task_repository import (
    AgentTaskRepository,
)
from app.repositories.mission_repository import (
    MissionRepository,
)
from app.schemas.mission import (
    MissionRequest,
    MissionStatus,
    PersistedMissionListResponse,
    PersistedMissionResponse,
    PersistedTaskListResponse,
    PersistedTaskResponse,
)
from app.services.mission_manager import (
    create_mission,
    get_mission,
    run_real_mission,
)
from app.workforce.orchestrator import (
    MissionExecutionError,
    MissionHasNoTasksError,
    MissionNotFoundError,
    WorkforceOrchestrator,
)


router = APIRouter(
    prefix="/missions",
    tags=["Missions"],
)


def get_workspace_mission_or_404(
    repository: MissionRepository,
    mission_uid: str,
    business_uid: str,
) -> Any:
    mission = repository.get_by_uid_and_business(
        mission_uid,
        business_uid,
    )

    if mission is None:
        raise HTTPException(
            status_code=404,
            detail="Persisted mission not found.",
        )

    return mission


def deserialize_json(
    value: str | dict[str, Any] | None,
) -> dict[str, Any] | None:
    """
    Safely convert a stored JSON value into a dictionary.
    """

    if value is None:
        return None

    if isinstance(value, dict):
        return value

    if not isinstance(value, str):
        return None

    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None

    if not isinstance(parsed, dict):
        return None

    return parsed


def build_mission_response(
    mission: Any,
) -> PersistedMissionResponse:
    """
    Convert a persisted Mission model into an API response.
    """

    return PersistedMissionResponse(
        mission_uid=mission.mission_uid,
        business_uid=mission.business_uid,
        objective_uid=mission.objective_uid,
        title=mission.title,
        objective=mission.objective,
        description=mission.description,
        status=mission.status,
        priority=mission.priority,
        progress=mission.progress,
        estimated_value=mission.estimated_value,
        expected_roi=mission.expected_roi,
        strategy_data=MissionRepository.deserialize_strategy(
            mission
        ),
        metadata=MissionRepository.deserialize_metadata(
            mission
        ),
        created_at=mission.created_at,
        updated_at=mission.updated_at,
        started_at=mission.started_at,
        completed_at=mission.completed_at,
    )


def build_task_response(
    task: Any,
) -> PersistedTaskResponse:
    """
    Convert a persisted AgentTask model into an API response.
    """

    return PersistedTaskResponse(
        task_uid=task.task_uid,
        mission_id=task.mission_id,
        agent_name=task.agent_name,
        task_type=task.task_type,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        progress=task.progress,
        sequence_number=task.sequence_number,
        depends_on_task_uid=task.depends_on_task_uid,
        input_data=deserialize_json(task.input_data),
        output_data=deserialize_json(task.output_data),
        error_message=task.error_message,
        retry_count=task.retry_count,
        max_retries=task.max_retries,
        estimated_value=task.estimated_value,
        created_at=task.created_at,
        updated_at=task.updated_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
    )


@router.post(
    "/start",
    response_model=MissionStatus,
)
async def start_mission(
    request: MissionRequest,
    business_uid: str = Depends(
        get_current_business_uid,
    ),
) -> MissionStatus:
    """
    Start the existing asynchronous lead-generation mission.
    """

    mission = create_mission(
        business_uid=business_uid,
    )

    asyncio.create_task(
        run_real_mission(
            mission["mission_id"],
            request,
            business_uid,
        )
    )

    return mission


@router.get(
    "",
    response_model=PersistedMissionListResponse,
)
def list_persisted_missions(
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid,
    ),
) -> PersistedMissionListResponse:
    """
    Return persisted missions for the Admin Explorer.
    """

    repository = MissionRepository(db)

    missions = repository.list_by_business(
        business_uid,
        limit=limit,
        offset=offset,
    )

    return PersistedMissionListResponse(
        missions=[
            build_mission_response(mission)
            for mission in missions
        ],
        count=len(missions),
    )


@router.post(
    "/{mission_uid}/execute",
)
def execute_persisted_mission(
    mission_uid: str,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid,
    ),
) -> dict[str, Any]:
    """
    Execute all eligible persisted tasks for a mission.
    """

    repository = MissionRepository(db)
    get_workspace_mission_or_404(
        repository,
        mission_uid,
        business_uid,
    )

    orchestrator = WorkforceOrchestrator(db)

    try:
        return orchestrator.execute_mission(
            mission_uid
        )

    except MissionNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except MissionHasNoTasksError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except MissionExecutionError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.get(
    "/{mission_uid}/tasks",
    response_model=PersistedTaskListResponse,
)
def list_persisted_mission_tasks(
    mission_uid: str,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid,
    ),
) -> PersistedTaskListResponse:
    """
    Return all persisted tasks belonging to one mission.
    """

    mission_repository = MissionRepository(db)

    get_workspace_mission_or_404(
        mission_repository,
        mission_uid,
        business_uid,
    )

    task_repository = AgentTaskRepository(db)

    tasks = task_repository.list_by_mission(
        mission_uid
    )

    return PersistedTaskListResponse(
        tasks=[
            build_task_response(task)
            for task in tasks
        ],
        count=len(tasks),
    )


@router.get(
    "/{mission_id}",
    response_model=MissionStatus,
)
async def mission_status(
    mission_id: str,
    business_uid: str = Depends(
        get_current_business_uid,
    ),
) -> MissionStatus:
    """
    Return the status of an existing asynchronous mission.
    """

    mission = get_mission(
        mission_id
    )

    if (
        mission is None
        or mission.get("business_uid")
        != business_uid
    ):
        raise HTTPException(
            status_code=404,
            detail=(
                "Mission not found. "
                "Use the complete Mission ID."
            ),
        )

    return mission
