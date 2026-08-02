from typing import Any

from sqlalchemy.orm import Session

from app.database.models import AgentTask, Mission
from app.repositories.agent_task_repository import (
    AgentTaskRepository,
)
from app.repositories.mission_event_repository import (
    MissionEventRepository,
)
from app.repositories.mission_repository import MissionRepository
from app.workforce.executive_router import ExecutiveRouter
from app.realtime.mission_event_publisher import (
    mission_event_publisher,
)


class MissionNotFoundError(Exception):
    """
    Raised when a requested persisted mission does not exist.
    """


class MissionHasNoTasksError(Exception):
    """
    Raised when a mission exists but has no executive tasks.
    """


class MissionExecutionError(Exception):
    """
    Raised when the mission cannot complete successfully.
    """


class WorkforceOrchestrator:
    """
    Executes persisted mission tasks through Nestora's
    executive workforce.

    Responsibilities:

    - Load a mission and its tasks.
    - Respect task sequence and dependencies.
    - Route tasks to the appropriate executive.
    - Persist task outputs.
    - Share completed executive outputs with later tasks.
    - Track task and mission progress.
    - Record immutable mission execution events.
    - Mark the mission completed, blocked, or failed.
    """

    def __init__(
        self,
        db: Session,
        executive_router: ExecutiveRouter | None = None,
    ) -> None:
        self._db = db
        self._mission_repository = MissionRepository(db)
        self._mission_event_repository = MissionEventRepository(db)
        self._task_repository = AgentTaskRepository(db)
        self._executive_router = (
            executive_router or ExecutiveRouter()
        )

    def _record_event(
        self,
        *,
        mission_uid: str,
        executive: str,
        event_type: str,
        status: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        """
        Persist a mission event and publish it to realtime subscribers.
        """
        print(f"RECORD EVENT: {event_type} | {message}")

        event = self._mission_event_repository.create_event(
            mission_uid=mission_uid,
            executive=executive,
            event_type=event_type,
            status=status,
            message=message,
            metadata=metadata or {},
        )

        event_data = {
            "event_uid": getattr(event, "event_uid", None),
            "mission_uid": mission_uid,
            "executive": executive,
            "event_type": event_type,
            "status": status,
            "message": message,
            "metadata": metadata or {},
            "created_at": (
                event.created_at.isoformat()
                if getattr(event, "created_at", None)
                else None
            ),
        }

        mission_event_publisher.publish(event_data)

        return event

    def execute_mission(
        self,
        mission_uid: str,
    ) -> dict[str, Any]:
        mission = self._mission_repository.get_by_uid(
            mission_uid
        )

        if mission is None:
            raise MissionNotFoundError(
                f"Mission '{mission_uid}' was not found."
            )

        tasks = self._task_repository.list_by_mission(
            mission_uid
        )

        if not tasks:
            raise MissionHasNoTasksError(
                f"Mission '{mission_uid}' has no tasks."
            )

        if mission.status == "completed":
            return self._build_execution_summary(
                mission=mission,
                tasks=tasks,
                message="Mission was already completed.",
            )

        self._mission_repository.mark_running(mission_uid)

        self._record_event(
            mission_uid=mission_uid,
            executive="CEO",
            event_type="mission_started",
            status="running",
            message=f"Mission '{mission.title}' started.",
            metadata={
                "business_uid": mission.business_uid,
                "title": mission.title,
                "priority": mission.priority,
                "task_count": len(tasks),
            },
        )

        self._update_mission_progress(
            mission_uid=mission_uid,
            tasks=tasks,
        )

        try:
            for task in tasks:
                if task.status == "completed":
                    continue

                if not self._dependency_is_complete(
                    task=task,
                    tasks=tasks,
                ):
                    continue

                self._execute_task(
                    task=task,
                    mission=mission,
                )

                tasks = self._task_repository.list_by_mission(
                    mission_uid
                )

                self._update_mission_progress(
                    mission_uid=mission_uid,
                    tasks=tasks,
                )

            tasks = self._task_repository.list_by_mission(
                mission_uid
            )

            failed_tasks = [
                task
                for task in tasks
                if task.status == "failed"
            ]

            incomplete_tasks = [
                task
                for task in tasks
                if task.status != "completed"
            ]

            if failed_tasks:
                raise MissionExecutionError(
                    f"{len(failed_tasks)} mission task(s) failed."
                )

            if incomplete_tasks:
                self._mission_repository.update_status(
                    mission_uid,
                    "blocked",
                )

                self._record_event(
                    mission_uid=mission_uid,
                    executive="CEO",
                    event_type="mission_blocked",
                    status="blocked",
                    message=(
                        "Mission execution paused because one or "
                        "more task dependencies are incomplete."
                    ),
                    metadata={
                        "incomplete_task_count": len(
                            incomplete_tasks
                        ),
                        "incomplete_task_uids": [
                            task.task_uid
                            for task in incomplete_tasks
                        ],
                    },
                )

                return self._build_execution_summary(
                    mission=self._require_mission(mission_uid),
                    tasks=tasks,
                    message=(
                        "Mission execution paused because one or "
                        "more task dependencies are incomplete."
                    ),
                )

            self._mission_repository.mark_completed(
                mission_uid
            )

            self._record_event(
                mission_uid=mission_uid,
                executive="CEO",
                event_type="mission_completed",
                status="completed",
                message=f"Mission '{mission.title}' completed successfully.",
                metadata={
                    "task_count": len(tasks),
                    "completed_task_count": len(tasks),
                    "progress": 100,
                },
            )

            return self._build_execution_summary(
                mission=self._require_mission(mission_uid),
                tasks=self._task_repository.list_by_mission(
                    mission_uid
                ),
                message="Mission completed successfully.",
            )

        except MissionExecutionError as exc:
            self._mission_repository.mark_failed(
                mission_uid
            )

            self._record_event(
                mission_uid=mission_uid,
                executive="CEO",
                event_type="mission_failed",
                status="failed",
                message=str(exc),
                metadata={
                    "error": str(exc),
                },
            )

            raise

        except Exception as exc:
            self._mission_repository.mark_failed(
                mission_uid
            )

            self._record_event(
                mission_uid=mission_uid,
                executive="CEO",
                event_type="mission_failed",
                status="failed",
                message=f"Mission execution failed: {exc}",
                metadata={
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                },
            )

            raise MissionExecutionError(
                f"Mission execution failed: {exc}"
            ) from exc

    def _execute_task(
        self,
        *,
        task: AgentTask,
        mission: Mission,
    ) -> None:
        self._task_repository.mark_running(
            task.task_uid
        )

        self._record_event(
            mission_uid=mission.mission_uid,
            executive=task.agent_name,
            event_type="task_started",
            status="running",
            message=f"Task '{task.title}' started.",
            metadata={
                "task_uid": task.task_uid,
                "task_type": task.task_type,
                "sequence_number": task.sequence_number,
                "depends_on_task_uid": (
                    task.depends_on_task_uid
                ),
            },
        )

        try:
            input_data = (
                self._task_repository.deserialize_input(task)
            )

            executive_context = self._build_executive_context(
                mission_uid=mission.mission_uid,
                current_task=task,
            )

            enriched_input = {
                **input_data,
                "mission_uid": mission.mission_uid,
                "business_uid": mission.business_uid,
                "mission_title": mission.title,
                "mission_objective": mission.objective,
                "mission_description": mission.description,
                "mission_priority": mission.priority,
                "estimated_mission_value": (
                    mission.estimated_value
                ),
                "expected_roi": mission.expected_roi,
                "executive_context": executive_context,
            }

            output = self._executive_router.execute_task(
                agent_name=task.agent_name,
                title=task.title,
                description=task.description,
                input_data=enriched_input,
            )

            self._task_repository.mark_completed(
                task.task_uid,
                output,
            )

            self._record_event(
                mission_uid=mission.mission_uid,
                executive=task.agent_name,
                event_type="task_completed",
                status="completed",
                message=f"Task '{task.title}' completed successfully.",
                metadata={
                    "task_uid": task.task_uid,
                    "task_type": task.task_type,
                    "sequence_number": task.sequence_number,
                },
            )

        except Exception as exc:
            self._task_repository.mark_failed(
                task.task_uid,
                str(exc),
            )

            self._record_event(
                mission_uid=mission.mission_uid,
                executive=task.agent_name,
                event_type="task_failed",
                status="failed",
                message=f"Task '{task.title}' failed: {exc}",
                metadata={
                    "task_uid": task.task_uid,
                    "task_type": task.task_type,
                    "sequence_number": task.sequence_number,
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                },
            )

            raise MissionExecutionError(
                f"Task '{task.task_uid}' failed: {exc}"
            ) from exc

    def _build_executive_context(
        self,
        *,
        mission_uid: str,
        current_task: AgentTask,
    ) -> dict[str, Any]:
        """
        Build shared context from previously completed tasks.

        The first executive receives an empty dictionary.

        Later executives receive the outputs of all completed tasks
        with a lower sequence number than the current task.
        """

        mission_tasks = (
            self._task_repository.list_by_mission(
                mission_uid
            )
        )

        completed_previous_tasks = sorted(
            (
                task
                for task in mission_tasks
                if task.status == "completed"
                and task.task_uid != current_task.task_uid
                and (
                    task.sequence_number or 0
                ) < (
                    current_task.sequence_number or 0
                )
            ),
            key=lambda task: task.sequence_number or 0,
        )

        executive_context: dict[str, Any] = {}

        for completed_task in completed_previous_tasks:
            output_data = (
                self._task_repository.deserialize_output(
                    completed_task
                )
            )

            context_key = completed_task.agent_name

            if context_key in executive_context:
                context_key = (
                    f"{completed_task.agent_name}_"
                    f"{completed_task.sequence_number}"
                )

            executive_context[context_key] = {
                "task_uid": completed_task.task_uid,
                "agent_name": completed_task.agent_name,
                "task_title": completed_task.title,
                "sequence_number": (
                    completed_task.sequence_number
                ),
                "output_data": output_data,
            }

        return executive_context

    def _dependency_is_complete(
        self,
        *,
        task: AgentTask,
        tasks: list[AgentTask],
    ) -> bool:
        dependency_uid = task.depends_on_task_uid

        if not dependency_uid:
            return True

        dependency = next(
            (
                candidate
                for candidate in tasks
                if candidate.task_uid == dependency_uid
            ),
            None,
        )

        if dependency is None:
            return False

        return dependency.status == "completed"

    def _update_mission_progress(
        self,
        *,
        mission_uid: str,
        tasks: list[AgentTask],
    ) -> int:
        if not tasks:
            progress = 0

        else:
            total_progress = sum(
                max(
                    0,
                    min(task.progress or 0, 100),
                )
                for task in tasks
            )

            progress = round(
                total_progress / len(tasks)
            )

        self._mission_repository.update_progress(
            mission_uid,
            progress,
        )

        return progress

    def _require_mission(
        self,
        mission_uid: str,
    ) -> Mission:
        mission = self._mission_repository.get_by_uid(
            mission_uid
        )

        if mission is None:
            raise MissionNotFoundError(
                f"Mission '{mission_uid}' was not found."
            )

        return mission

    def _build_execution_summary(
        self,
        *,
        mission: Mission,
        tasks: list[AgentTask],
        message: str,
    ) -> dict[str, Any]:
        completed_count = sum(
            1
            for task in tasks
            if task.status == "completed"
        )

        failed_count = sum(
            1
            for task in tasks
            if task.status == "failed"
        )

        pending_count = sum(
            1
            for task in tasks
            if task.status in {
                "pending",
                "running",
            }
        )

        return {
            "mission_uid": mission.mission_uid,
            "business_uid": mission.business_uid,
            "title": mission.title,
            "status": mission.status,
            "progress": mission.progress,
            "message": message,
            "task_summary": {
                "total": len(tasks),
                "completed": completed_count,
                "failed": failed_count,
                "pending": pending_count,
            },
            "tasks": [
                {
                    "task_uid": task.task_uid,
                    "agent_name": task.agent_name,
                    "title": task.title,
                    "status": task.status,
                    "progress": task.progress,
                    "sequence_number": (
                        task.sequence_number
                    ),
                    "depends_on_task_uid": (
                        task.depends_on_task_uid
                    ),
                    "output_data": (
                        self._task_repository.deserialize_output(
                            task
                        )
                    ),
                    "error_message": task.error_message,
                }
                for task in tasks
            ],
        }