from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    Field,
)


class MissionEventResponse(
    BaseModel
):
    event_uid: str
    executive: str
    event_type: str
    status: str
    message: str
    metadata: (
        dict[str, Any] | None
    ) = None
    created_at: datetime


class MissionEventListResponse(
    BaseModel
):
    mission_uid: str
    count: int
    events: list[
        MissionEventResponse
    ] = Field(
        default_factory=list
    )