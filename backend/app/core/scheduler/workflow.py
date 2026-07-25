from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from app.core.scheduler.models import SchedulerTask


class Workflow(BaseModel):
    """
    Execution plan for completing a mission.

    A workflow belongs to exactly one mission and contains
    one or more scheduler tasks.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    mission_id: str

    name: str

    description: str = ""

    tasks: list[SchedulerTask] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def task_count(self) -> int:
        return len(self.tasks)

    def add_task(self, task: SchedulerTask) -> None:
        self.tasks.append(task)
        self.updated_at = datetime.utcnow()

    def remove_task(self, task_id: str) -> bool:
        original_count = len(self.tasks)

        self.tasks = [
            task
            for task in self.tasks
            if task.id != task_id
        ]

        removed = len(self.tasks) != original_count

        if removed:
            self.updated_at = datetime.utcnow()

        return removed

    def get_task(self, task_id: str) -> SchedulerTask | None:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None


class WorkflowResult(BaseModel):
    """
    Final outcome after a workflow completes.
    """

    workflow_id: str

    success: bool

    completed_tasks: int = 0

    failed_tasks: int = 0

    execution_time_seconds: float = 0.0

    metadata: dict[str, Any] = Field(default_factory=dict)

    completed_at: datetime = Field(default_factory=datetime.utcnow)