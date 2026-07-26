from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.core.execution.dispatcher import (
    DispatchResult,
    ExecutiveDispatcher,
    executive_dispatcher,
)
from app.core.missions.models import Mission
from app.core.missions.registry import MissionRegistry, mission_registry
from app.core.scheduler.models import SchedulerResult
from app.core.scheduler.scheduler import (
    ExecutiveScheduler,
    executive_scheduler,
)
from app.core.scheduler.workflow import Workflow, WorkflowResult
from app.executives.ceo.mission_builder import (
    CEOMissionBuilder,
    MissionBuildResult,
)
from app.executives.ceo.models import ExecutivePlan


class ExecutionServiceError(Exception):
    """Base exception for execution-service failures."""


class ExecutionStalledError(ExecutionServiceError):
    """Raised when a workflow cannot make further progress."""


@dataclass(slots=True)
class ExecutionResult:
    """
    Complete result of executing one CEO-generated business mission.
    """

    mission: Mission
    workflow: Workflow
    success: bool

    dispatch_results: list[DispatchResult] = field(
        default_factory=list
    )

    workflow_result: WorkflowResult | None = None
    scheduler_result: SchedulerResult | None = None

    error: str | None = None

    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def execution_time_seconds(self) -> float:
        return max(
            0.0,
            (self.completed_at - self.started_at).total_seconds(),
        )

    @property
    def completed_task_count(self) -> int:
        return sum(
            result.success
            for result in self.dispatch_results
        )

    @property
    def failed_task_count(self) -> int:
        return sum(
            not result.success
            for result in self.dispatch_results
        )


class ExecutionService:
    """
    Coordinates end-to-end execution of a CEO ExecutivePlan.

    Flow:

    ExecutivePlan
        -> CEOMissionBuilder
        -> Mission Registry
        -> Executive Scheduler
        -> Executive Dispatcher
        -> ExecutionResult
    """

    def __init__(
        self,
        mission_builder: CEOMissionBuilder | None = None,
        missions: MissionRegistry | None = None,
        scheduler: ExecutiveScheduler | None = None,
        dispatcher: ExecutiveDispatcher | None = None,
    ) -> None:
        self.mission_builder = (
            mission_builder or CEOMissionBuilder()
        )
        self.missions = missions or mission_registry
        self.scheduler = scheduler or executive_scheduler
        self.dispatcher = dispatcher or executive_dispatcher

    async def execute_plan(
        self,
        plan: ExecutivePlan,
    ) -> ExecutionResult:
        """
        Build and execute a mission from a CEO ExecutivePlan.
        """
        started_at = datetime.utcnow()
        build_result = self.mission_builder.build(plan)

        try:
            self._register_build_result(build_result)

            dispatch_results = await self._execute_workflow(
                build_result.workflow
            )

            workflow_result = self.scheduler.get_result(
                build_result.workflow.id
            )

            scheduler_result = (
                self.scheduler.build_scheduler_result(
                    build_result.workflow.id
                )
            )

            success = (
                workflow_result is not None
                and workflow_result.success
                and scheduler_result.success
            )

            return ExecutionResult(
                mission=build_result.mission,
                workflow=build_result.workflow,
                success=success,
                dispatch_results=dispatch_results,
                workflow_result=workflow_result,
                scheduler_result=scheduler_result,
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )

        except Exception as exc:
            return ExecutionResult(
                mission=build_result.mission,
                workflow=build_result.workflow,
                success=False,
                error=f"{type(exc).__name__}: {exc}",
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )

    def _register_build_result(
        self,
        build_result: MissionBuildResult,
    ) -> None:
        """
        Register the mission and its workflow.
        """
        self.missions.add(build_result.mission)

        self.scheduler.register_workflow(
            build_result.workflow
        )

        self.scheduler.start_workflow(
            build_result.workflow.id
        )

    async def _execute_workflow(
        self,
        workflow: Workflow,
    ) -> list[DispatchResult]:
        """
        Execute all runnable tasks until the workflow finishes.
        """
        dispatch_results: list[DispatchResult] = []

        while not self.scheduler.workflow_is_finished(
            workflow.id
        ):
            task = self.scheduler.get_next_task(workflow.id)

            if task is None:
                raise ExecutionStalledError(
                    f"Workflow '{workflow.id}' cannot make "
                    f"further progress."
                )

            dispatch_result = await self.dispatcher.dispatch(task)
            dispatch_results.append(dispatch_result)

            if dispatch_result.success:
                self.scheduler.complete_task(
                    workflow_id=workflow.id,
                    task_id=task.id,
                    result=dispatch_result.result,
                )
            else:
                self.scheduler.fail_task(
                    workflow_id=workflow.id,
                    task_id=task.id,
                    error=(
                        dispatch_result.error
                        or "Executive dispatch failed."
                    ),
                )

        return dispatch_results

    def get_mission(self, mission_id: str) -> Mission | None:
        """Return a registered mission."""
        return self.missions.get(mission_id)

    def get_workflow(self, workflow_id: str) -> Workflow:
        """Return a registered workflow."""
        return self.scheduler.get_workflow(workflow_id)

    def clear(self) -> None:
        """Clear execution state used by the service."""
        self.missions.clear()
        self.scheduler.clear()


execution_service = ExecutionService()