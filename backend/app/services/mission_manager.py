from app.database.database import SessionLocal
from app.services.mission_activity import log_mission_activity
from app.services.mission_executor import MissionExecutor
from app.services.mission_state import (
    MISSIONS,
    build_default_agents,
    create_mission,
    fail_running_agents,
    get_mission,
    update_agent,
    update_mission,
)
from app.services.mission_task_planner import create_mission_task_plan
from app.services.mission_task_runtime import fail_mission_task


async def run_real_mission(
    mission_id,
    request,
    business_uid,
):
    """
    Plan and execute one Nestora mission.

    This module now acts only as the top-level orchestrator.
    The detailed business workflow lives in MissionExecutor.
    """
    db = SessionLocal()
    executor = None

    try:
        mission = get_mission(mission_id)

        if mission is None:
            raise ValueError(
                f"Mission {mission_id} was not found."
            )

        # ---------------------------------------------------------
        # Build the persistent execution plan
        # ---------------------------------------------------------

        mission_tasks = create_mission_task_plan(
            db,
            mission_id,
            request,
        )

        update_mission(
            mission_id,
            task_count=len(mission_tasks),
            status="running",
            progress=3,
            current_step="CEO Agent is planning the mission",
        )

        log_mission_activity(
            mission,
            "CEO Agent",
            (
                f"Created execution plan with "
                f"{len(mission_tasks)} tasks."
            ),
        )

        log_mission_activity(
            mission,
            "CEO Agent",
            "Mission started.",
        )

        # ---------------------------------------------------------
        # CEO planning state
        # ---------------------------------------------------------

        update_agent(
            mission_id,
            "CEO Agent",
            status="running",
            progress=50,
            current_task="Planning mission workflow",
        )

        update_agent(
            mission_id,
            "CEO Agent",
            status="completed",
            progress=100,
            current_task="Mission plan completed",
        )

        log_mission_activity(
            mission,
            "CEO Agent",
            "Mission plan completed.",
        )

        # ---------------------------------------------------------
        # Execute the mission workflow
        # ---------------------------------------------------------

        executor = MissionExecutor(
            db=db,
            mission_id=mission_id,
            request=request,
            business_uid=business_uid,
        )

        return await executor.execute()

    except Exception as error:
        db.rollback()

        print(
            f"Real mission failed for "
            f"{mission_id}: {error}"
        )

        active_task_type = (
            executor.active_task_type
            if executor is not None
            else None
        )

        if active_task_type:
            try:
                fail_mission_task(
                    db,
                    mission_id,
                    active_task_type,
                    str(error),
                )
            except Exception as task_error:
                db.rollback()

                print(
                    "Could not mark the persistent task "
                    f"as failed: {task_error}"
                )

        fail_running_agents(
            mission_id,
            message=(
                "Agent stopped because the mission failed"
            ),
        )

        mission = get_mission(mission_id)

        if mission is not None:
            log_mission_activity(
                mission,
                "CEO Agent",
                f"Mission failed: {error}",
            )

        update_mission(
            mission_id,
            status="failed",
            progress=100,
            current_step=f"Mission failed: {error}",
        )

        return {
            "mission_id": mission_id,
            "status": "failed",
            "error": str(error),
        }

    finally:
        db.close()
