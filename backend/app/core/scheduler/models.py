from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from app.core.scheduler.status import TaskStatus


class SchedulerTask(BaseModel):
    """
    A single executable unit managed by the scheduler.

    A task may represent an executive, worker, tool call,
    automation, or any future executable component.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    mission_id: str

    name: str

    task_type: str

    executor: str

    payload: dict[str, Any] = Field(default_factory=dict)

    dependencies: list[str] = Field(default_factory=list)

    status: TaskStatus = TaskStatus.PENDING

    priority: int = Field(default=100, ge=1)

    max_retries: int = Field(default=0, ge=0)

    retry_count: int = Field(default=0, ge=0)

    result: Any | None = None

    error: str | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    updated_at: datetime = Field(default_factory=datetime.utcnow)

    started_at: datetime | None = None

    completed_at: datetime | None = None

    @field_validator(
        "mission_id",
        "name",
        "task_type",
        "executor",
    )
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        clean_value = value.strip()

        if not clean_value:
            raise ValueError("Value cannot be empty.")

        return clean_value

    @field_validator("dependencies")
    @classmethod
    def normalize_dependencies(
        cls,
        dependencies: list[str],
    ) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()

        for dependency in dependencies:
            clean_dependency = dependency.strip()

            if not clean_dependency:
                continue

            if clean_dependency not in seen:
                normalized.append(clean_dependency)
                seen.add(clean_dependency)

        return normalized

    @property
    def can_retry(self) -> bool:
        """
        Return True when the task has remaining retry attempts.
        """
        return self.retry_count < self.max_retries


class SchedulerResult(BaseModel):
    """
    Final execution summary for a scheduled workflow.
    """

    mission_id: str

    success: bool

    task_results: dict[str, Any] = Field(default_factory=dict)

    failed_tasks: list[str] = Field(default_factory=list)

    completed_at: datetime = Field(default_factory=datetime.utcnow)