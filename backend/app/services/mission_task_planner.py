from sqlalchemy.orm import Session

from app.schemas.agent_task import AgentTaskCreate
from app.schemas.mission import MissionRequest
from app.services.agent_task_service import (
    create_agent_task,
    get_mission_tasks,
)
from app.services.mission_planner import build_execution_plan


def create_mission_task_plan(
    db: Session,
    mission_id: str,
    request: MissionRequest,
):
    """
    Build and save the complete task plan for a mission.

    Existing mission tasks are returned instead of being duplicated.
    """

    existing_tasks = get_mission_tasks(
        db,
        mission_id,
    )

    if existing_tasks:
        return existing_tasks

    execution_plan = build_execution_plan(request)

    created_tasks = []
    previous_task_uid = None

    for plan_item in execution_plan:
        task_data = AgentTaskCreate(
            mission_id=mission_id,
            agent_name=plan_item["agent"],
            task_type=plan_item["task_type"],
            title=plan_item["title"],
            description=plan_item.get("description"),
            priority=plan_item.get(
                "priority",
                "medium",
            ),
            sequence_number=plan_item.get(
                "sequence",
                0,
            ),
            depends_on_task_uid=previous_task_uid,
        )

        task = create_agent_task(
            db,
            task_data,
            input_data={
                "business_type": request.business_type,
                "location": request.location,
                "quantity": request.quantity,
                "minimum_quality": request.minimum_quality,
                "priority_filter": request.priority_filter,
                "analyze_websites": request.analyze_websites,
                "generate_outreach": request.generate_outreach,
            },
        )

        created_tasks.append(task)
        previous_task_uid = task.task_uid

    return created_tasks