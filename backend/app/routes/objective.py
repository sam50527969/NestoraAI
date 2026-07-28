from __future__ import annotations

from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.mission.planner import MissionPlanner
from app.objective.exceptions import (
    ObjectiveError,
    ObjectiveExecutionError,
    ObjectiveValidationError,
)
from app.objective.models import BusinessObjective
from app.repositories.agent_task_repository import (
    AgentTaskRepository,
)
from app.repositories.business_repository import (
    BusinessRepository,
)
from app.repositories.mission_repository import (
    MissionRepository,
)
from app.schemas.objective import (
    ObjectiveRequest,
    ObjectiveResponse,
    OpportunityResponse,
    StrategyResponse,
)
from app.services.objective_service import ObjectiveService


router = APIRouter(
    prefix="/ceo",
    tags=["AI CEO"],
)


@router.post(
    "/objective",
    response_model=ObjectiveResponse,
    status_code=status.HTTP_200_OK,
)
def analyze_objective(
    request: ObjectiveRequest,
    db: Session = Depends(get_db),
) -> ObjectiveResponse:
    """
    Analyze a business objective and create a planned mission.

    Processing flow:

    1. Retrieve the persisted business profile.
    2. Process the objective through the Objective Engine.
    3. Convert the generated strategy into a MissionPlan.
    4. Persist the mission.
    5. Persist the mission's executive tasks.
    6. Return the existing objective analysis response.

    The created mission remains in the "planned" state and its tasks
    remain "pending". No task execution begins automatically.
    """

    business_id = request.business_id.strip()
    objective_text = request.objective.strip()

    if not business_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business ID is required.",
        )

    if not objective_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Objective is required.",
        )

    business_repository = BusinessRepository(db)

    try:
        business = business_repository.get_by_uid(
            business_id,
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The business profile could not be retrieved.",
        ) from exc

    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business '{business_id}' was not found.",
        )

    objective = BusinessObjective(
        id=str(uuid4()),
        title=objective_text,
        description=objective_text,
        business_id=business.id,
        created_by="business_owner",
        metadata={
            "source": "ceo_objective_api",
        },
    )

    objective_service = ObjectiveService()

    try:
        result = objective_service.process_objective(
            business=business,
            objective=objective,
        )

    except ObjectiveValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except ObjectiveExecutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    except ObjectiveError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    planner = MissionPlanner()

    try:
        mission_plan = planner.create_plan(
            objective=objective_text,
            engine_result=result,
        )

        mission_repository = MissionRepository(db)

        mission = mission_repository.create(
            business_uid=business_id,
            objective_uid=objective.id,
            title=mission_plan.title,
            objective=mission_plan.objective,
            description=mission_plan.description,
            status="planned",
            priority=mission_plan.priority,
            estimated_value=mission_plan.estimated_value,
            expected_roi=mission_plan.expected_roi,
            strategy_data=mission_plan.strategy_data,
            metadata=mission_plan.metadata,
        )

        task_repository = AgentTaskRepository(db)

        previous_task_uid: str | None = None

        for sequence_number, task_plan in enumerate(
            mission_plan.tasks,
            start=1,
        ):
            task = task_repository.create(
                mission_id=mission.mission_uid,
                executive=task_plan.executive,
                title=task_plan.title,
                description=task_plan.description,
                priority=task_plan.priority,
                sequence_number=sequence_number,
                depends_on=previous_task_uid,
                estimated_value=task_plan.estimated_value,
                input_data={
                    "business_uid": business_id,
                    "objective_uid": objective.id,
                    "objective": objective_text,
                    "mission_uid": mission.mission_uid,
                    "sequence_number": sequence_number,
                },
            )

            previous_task_uid = task.task_uid

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "The objective was analyzed, but its mission "
                "could not be created."
            ),
        ) from exc

    opportunities = [
        OpportunityResponse(
            title=opportunity.title,
            description=opportunity.description,
            estimated_value=opportunity.estimated_value,
            confidence=opportunity.confidence,
            executives=list(opportunity.executives),
        )
        for opportunity in result.analysis.opportunities
    ]

    strategy = StrategyResponse(
        title=result.strategy.title,
        summary=result.strategy.summary,
        confidence=result.strategy.confidence,
        estimated_roi=result.strategy.estimated_roi,
        missions=list(result.strategy.missions),
        executives=list(result.strategy.executives),
        risks=list(result.strategy.risks),
    )

    return ObjectiveResponse(
        success=True,
       mission_uid=mission.mission_uid,
       mission_status=mission.status,
       opportunities=opportunities,
       strategy=strategy,
    )