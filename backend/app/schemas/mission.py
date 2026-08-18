from __future__ import annotations

from datetime import datetime
from typing import (
    Any,
    Literal,
)

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


MissionPriorityFilter = Literal[
    "all",
    "high",
    "medium",
    "low",
]


class MissionRequest(BaseModel):
    business_type: str = Field(
        min_length=1,
        max_length=120,
    )
    location: str = Field(
        min_length=1,
        max_length=200,
    )
    quantity: int = Field(
        default=20,
        ge=1,
        le=100,
    )
    analyze_websites: bool = True
    generate_outreach: bool = True
    minimum_quality: int = Field(
        default=60,
        ge=0,
        le=100,
    )
    priority_filter: (
        MissionPriorityFilter
    ) = "all"

    @field_validator(
        "business_type",
        "location",
        mode="before",
    )
    @classmethod
    def normalize_required_text(
        cls,
        value: object,
    ) -> str:
        if not isinstance(value, str):
            raise ValueError(
                "Value must be a string."
            )

        cleaned = value.strip()

        if not cleaned:
            raise ValueError(
                "Value must not be empty."
            )

        return cleaned

    @field_validator(
        "priority_filter",
        mode="before",
    )
    @classmethod
    def normalize_priority_filter(
        cls,
        value: object,
    ) -> object:
        if isinstance(value, str):
            return value.strip().lower()

        return value


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
    current_task: str = (
        "Waiting for work"
    )


class MissionActivityItem(BaseModel):
    time: str
    agent: str
    message: str


class MissionStatus(BaseModel):
    mission_id: str
    status: str
    progress: int = Field(
        ge=0,
        le=100,
    )
    current_step: str
    searched: int = Field(ge=0)
    analyzed: int = Field(ge=0)
    outreach_generated: int = Field(
        ge=0
    )
    agents: list[
        MissionAgentStatus
    ] = Field(
        default_factory=list
    )
    activity: list[
        MissionActivityItem
    ] = Field(
        default_factory=list
    )


class PersistedMissionResponse(
    BaseModel
):
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

    strategy_data: (
        dict[str, Any] | None
    ) = None
    metadata: (
        dict[str, Any] | None
    ) = None

    created_at: datetime
    updated_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None


class PersistedMissionListResponse(
    BaseModel
):
    missions: list[
        PersistedMissionResponse
    ] = Field(
        default_factory=list
    )
    count: int


class PersistedTaskResponse(
    BaseModel
):
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
    depends_on_task_uid: (
        str | None
    ) = None

    input_data: (
        dict[str, Any] | None
    ) = None
    output_data: (
        dict[str, Any] | None
    ) = None
    error_message: str | None = None

    retry_count: int
    max_retries: int
    estimated_value: float | None = None

    created_at: datetime
    updated_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None


class PersistedTaskListResponse(
    BaseModel
):
    tasks: list[
        PersistedTaskResponse
    ] = Field(
        default_factory=list
    )
    count: int