from __future__ import annotations

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
)


class AgentTaskCreate(BaseModel):
    mission_id: str
    agent_name: str
    task_type: str
    title: str
    description: str | None = None
    priority: str = "medium"
    sequence_number: int = 0
    depends_on_task_uid: (
        str | None
    ) = None


class AgentTaskUpdate(BaseModel):
    status: str | None = None
    progress: int | None = None
    output_data: str | None = None
    error_message: str | None = None


class AgentTaskResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    task_uid: str
    mission_id: str
    agent_name: str
    task_type: str
    title: str
    description: str | None
    status: str
    priority: str
    progress: int
    sequence_number: int
    depends_on_task_uid: (
        str | None
    )

    retry_count: int

    created_at: datetime
    updated_at: datetime

    started_at: datetime | None
    completed_at: datetime | None