from __future__ import annotations

from datetime import datetime
from typing import Any

from app.core.scheduler.graph import DependencyGraph
from app.core.scheduler.models import SchedulerResult, SchedulerTask
from app.core.scheduler.queue import ExecutionQueue
from app.core.scheduler.status import TaskStatus
from app.core.scheduler.workflow import Workflow, WorkflowResult


class SchedulerError(Exception):
    """Base exception for scheduler failures."""


class WorkflowNotFoundError(SchedulerError):
    """Raised when a requested workflow does not exist."""


class TaskNotFoundError(SchedulerError):
    """Raised when a requested scheduler task does not exist."""


class WorkflowAlreadyExistsError(SchedulerError):
    """Raised when a workflow with the same ID is registered twice."""


class ExecutiveScheduler:
    """
    Coordinates workflow validation, task readiness, execution order,
    task status changes, retries, and workflow result generation.

    This first version does not directly execute executives or tools.
    It manages orchestration state and exposes the next runnable task
    to a future dispatcher.
    """

    def __init__(self) -> None:
        self._workflows: dict[str, Workflow] = {}
        self._graphs: dict[str, DependencyGraph] = {}
        self._queues: dict[str, ExecutionQueue] = {}
        self._started_at: dict[str, datetime] = {}
        self._results: dict[str, WorkflowResult] = {}

    def register_workflow(self, workflow: Workflow) -> Workflow:
        """
        Validate and register a workflow.

        Every task must belong to the same mission as the workflow.
        """
        if workflow.id in self._workflows:
            raise WorkflowAlreadyExistsError(
                f"Workflow '{workflow.id}' is already registered."
            )

        if not workflow.tasks:
            raise ValueError("A workflow must contain at least one task.")

        graph = DependencyGraph()

        for task in workflow.tasks:
            if task.mission_id != workflow.mission_id:
                raise ValueError(
                    f"Task '{task.id}' belongs to mission "
                    f"'{task.mission_id}', not '{workflow.mission_id}'."
                )

            graph.add_task(task)

        graph.validate()

        self._workflows[workflow.id] = workflow
        self._graphs[workflow.id] = graph
        self._queues[workflow.id] = ExecutionQueue()

        self._refresh_ready_tasks(workflow.id)

        return workflow

    def get_workflow(self, workflow_id: str) -> Workflow:
        """Return a registered workflow."""
        workflow = self._workflows.get(workflow_id)

        if workflow is None:
            raise WorkflowNotFoundError(
                f"Workflow '{workflow_id}' was not found."
            )

        return workflow

    def list_workflows(self) -> list[Workflow]:
        """Return every registered workflow."""
        return list(self._workflows.values())

    def start_workflow(self, workflow_id: str) -> Workflow:
        """
        Start a workflow and prepare all dependency-free tasks.
        """
        workflow = self.get_workflow(workflow_id)

        if workflow_id not in self._started_at:
            self._started_at[workflow_id] = datetime.utcnow()

        self._refresh_ready_tasks(workflow_id)

        return workflow

    def get_next_task(
        self,
        workflow_id: str,
    ) -> SchedulerTask | None:
        """
        Return the next runnable task and mark it as RUNNING.
        """
        self.get_workflow(workflow_id)
        self._refresh_ready_tasks(workflow_id)

        queue = self._queues[workflow_id]

        while not queue.is_empty():
            task = queue.pop()

            if task is None:
                return None

            if task.status != TaskStatus.READY:
                continue

            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            task.updated_at = datetime.utcnow()

            return task

        return None

    def complete_task(
        self,
        workflow_id: str,
        task_id: str,
        result: Any = None,
    ) -> SchedulerTask:
        """
        Mark a running task as completed and unlock dependents.
        """
        task = self._get_task(workflow_id, task_id)

        if task.status != TaskStatus.RUNNING:
            raise SchedulerError(
                f"Task '{task.id}' cannot complete while its status is "
                f"'{task.status.value}'."
            )

        now = datetime.utcnow()

        task.status = TaskStatus.COMPLETED
        task.result = result
        task.error = None
        task.completed_at = now
        task.updated_at = now

        self._refresh_ready_tasks(workflow_id)
        self._finalize_if_finished(workflow_id)

        return task

    def fail_task(
        self,
        workflow_id: str,
        task_id: str,
        error: str,
    ) -> SchedulerTask:
        """
        Fail a running task or place it back into the queue for retry.
        """
        task = self._get_task(workflow_id, task_id)

        if task.status != TaskStatus.RUNNING:
            raise SchedulerError(
                f"Task '{task.id}' cannot fail while its status is "
                f"'{task.status.value}'."
            )

        clean_error = error.strip()

        if not clean_error:
            clean_error = "Unknown scheduler task failure."

        task.error = clean_error
        task.updated_at = datetime.utcnow()

        if task.can_retry:
            task.retry_count += 1
            task.status = TaskStatus.RETRYING
            task.status = TaskStatus.READY
            self._queues[workflow_id].push(task)
        else:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()

        self._update_blocked_tasks(workflow_id)
        self._finalize_if_finished(workflow_id)

        return task

    def cancel_task(
        self,
        workflow_id: str,
        task_id: str,
    ) -> SchedulerTask:
        """Cancel a task that has not completed."""
        task = self._get_task(workflow_id, task_id)

        if task.status.is_terminal:
            raise SchedulerError(
                f"Task '{task.id}' is already in terminal state "
                f"'{task.status.value}'."
            )

        now = datetime.utcnow()

        task.status = TaskStatus.CANCELLED
        task.completed_at = now
        task.updated_at = now

        self._update_blocked_tasks(workflow_id)
        self._finalize_if_finished(workflow_id)

        return task

    def cancel_workflow(self, workflow_id: str) -> WorkflowResult:
        """Cancel every unfinished task in a workflow."""
        workflow = self.get_workflow(workflow_id)
        now = datetime.utcnow()

        for task in workflow.tasks:
            if not task.status.is_terminal:
                task.status = TaskStatus.CANCELLED
                task.completed_at = now
                task.updated_at = now

        return self._create_result(workflow_id)

    def get_result(
        self,
        workflow_id: str,
    ) -> WorkflowResult | None:
        """Return the final workflow result if one exists."""
        self.get_workflow(workflow_id)
        return self._results.get(workflow_id)

    def workflow_is_finished(self, workflow_id: str) -> bool:
        """Return True when every task is terminal."""
        workflow = self.get_workflow(workflow_id)

        return all(task.status.is_terminal for task in workflow.tasks)

    def build_scheduler_result(
        self,
        workflow_id: str,
    ) -> SchedulerResult:
        """
        Build a detailed task-result summary for mission integration.
        """
        workflow = self.get_workflow(workflow_id)

        failed_tasks = [
            task.id
            for task in workflow.tasks
            if task.status in {
                TaskStatus.FAILED,
                TaskStatus.CANCELLED,
                TaskStatus.BLOCKED,
            }
        ]

        task_results = {
            task.id: task.result
            for task in workflow.tasks
            if task.status == TaskStatus.COMPLETED
        }

        return SchedulerResult(
            mission_id=workflow.mission_id,
            success=not failed_tasks and self.workflow_is_finished(workflow_id),
            task_results=task_results,
            failed_tasks=failed_tasks,
        )

    def clear(self) -> None:
        """Clear all workflows and scheduler state."""
        self._workflows.clear()
        self._graphs.clear()
        self._queues.clear()
        self._started_at.clear()
        self._results.clear()

    def _get_task(
        self,
        workflow_id: str,
        task_id: str,
    ) -> SchedulerTask:
        workflow = self.get_workflow(workflow_id)
        task = workflow.get_task(task_id)

        if task is None:
            raise TaskNotFoundError(
                f"Task '{task_id}' was not found in workflow "
                f"'{workflow_id}'."
            )

        return task

    def _refresh_ready_tasks(self, workflow_id: str) -> None:
        workflow = self.get_workflow(workflow_id)
        graph = self._graphs[workflow_id]
        queue = self._queues[workflow_id]

        for task in workflow.tasks:
            if task.status != TaskStatus.PENDING:
                continue

            dependencies = graph.get_dependencies(task.id)

            if all(
                dependency.status == TaskStatus.COMPLETED
                for dependency in dependencies
            ):
                queue.push(task)

    def _update_blocked_tasks(self, workflow_id: str) -> None:
        workflow = self.get_workflow(workflow_id)
        graph = self._graphs[workflow_id]

        changed = True

        while changed:
            changed = False

            for task in workflow.tasks:
                if task.status not in {
                    TaskStatus.PENDING,
                    TaskStatus.READY,
                }:
                    continue

                dependencies = graph.get_dependencies(task.id)

                if any(
                    dependency.status in {
                        TaskStatus.FAILED,
                        TaskStatus.CANCELLED,
                        TaskStatus.BLOCKED,
                    }
                    for dependency in dependencies
                ):
                    task.status = TaskStatus.BLOCKED
                    task.error = "A required dependency did not complete."
                    task.completed_at = datetime.utcnow()
                    task.updated_at = datetime.utcnow()
                    changed = True

    def _finalize_if_finished(self, workflow_id: str) -> None:
        if self.workflow_is_finished(workflow_id):
            self._create_result(workflow_id)

    def _create_result(self, workflow_id: str) -> WorkflowResult:
        workflow = self.get_workflow(workflow_id)

        completed_tasks = sum(
            task.status == TaskStatus.COMPLETED
            for task in workflow.tasks
        )

        failed_tasks = sum(
            task.status in {
                TaskStatus.FAILED,
                TaskStatus.CANCELLED,
                TaskStatus.BLOCKED,
            }
            for task in workflow.tasks
        )

        started_at = self._started_at.get(
            workflow_id,
            workflow.created_at,
        )

        execution_time_seconds = max(
            0.0,
            (datetime.utcnow() - started_at).total_seconds(),
        )

        result = WorkflowResult(
            workflow_id=workflow.id,
            success=(
                completed_tasks == len(workflow.tasks)
                and failed_tasks == 0
            ),
            completed_tasks=completed_tasks,
            failed_tasks=failed_tasks,
            execution_time_seconds=execution_time_seconds,
        )

        self._results[workflow_id] = result
        return result


executive_scheduler = ExecutiveScheduler()