from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MissionRequest(BaseModel):
    business_type: str
    location: str
    quantity: int = 20
    analyze_websites: bool = True
    generate_outreach: bool = True
    minimum_quality: int = Field(
        default=60,
        ge=0,
        le=100,
    )
    priority_filter: str = "all"


class MissionAgentStatus(BaseModel):
    name: str
    role: str
    icon: str
    status: str = "waiting"
    progress: int = Field(
        default=0,
        ge=0,
        le=100,
    )
    current_task: str = "Waiting for work"


class MissionActivityItem(BaseModel):
    time: str
    agent: str
    message: str


class MissionStatus(BaseModel):
    mission_id: str
    status: str
    progress: int
    current_step: str
    searched: int
    analyzed: int
    outreach_generated: int
    agents: list[MissionAgentStatus] = Field(
        default_factory=list
    )
    activity: list[MissionActivityItem] = Field(
        default_factory=list
    )


class PersistedMissionResponse(BaseModel):
    mission_uid: str
    business_uid: str
    objective_uid: str | None = None

    title: str
    objective: str
    description: str | None = None

    status: str
    priority: str
    progress: int

    estimated_value: float | None = None
    expected_roi: float | None = None

    strategy_data: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None

    created_at: datetime
    updated_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None


class PersistedMissionListResponse(BaseModel):
    missions: list[PersistedMissionResponse] = Field(
        default_factory=list
    )
    count: int


class PersistedTaskResponse(BaseModel):
    task_uid: str
    mission_id: str

    agent_name: str
    task_type: str

    title: str
    description: str | None = None

    status: str
    priority: str
    progress: int

    sequence_number: int
    depends_on_task_uid: str | None = None

    input_data: dict[str, Any] | None = None
    output_data: dict[str, Any] | None = None
    error_message: str | None = None

    retry_count: int
    max_retries: int
    estimated_value: float | None = None

    created_at: datetime
    updated_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None


class PersistedTaskListResponse(BaseModel):
    tasks: list[PersistedTaskResponse] = Field(
        default_factory=list
    )
    count: int