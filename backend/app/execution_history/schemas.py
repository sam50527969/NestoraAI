from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class CEOExecutionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    execution_uid: str
    approval_uid: str

    mission_id: str | None = None
    workflow_id: str | None = None

    objective: str
    status: str
    success: bool

    completed_task_count: int
    failed_task_count: int

    error: str | None = None

    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class CEOExecutionDetailResponse(
    CEOExecutionResponse
):
    result: dict[str, Any] | None = None


class CEOExecutionListResponse(BaseModel):
    executions: list[
        CEOExecutionResponse
    ] = Field(
        default_factory=list,
    )

    count: int
    limit: int
    offset: int