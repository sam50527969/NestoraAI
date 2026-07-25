from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from app.core.missions.status import MissionStatus


class Mission(BaseModel):
    """
    A business objective created by the CEO and executed
    by one or more specialist executives.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    title: str

    objective: str

    created_by: str = "CEO"

    assigned_to: list[str] = Field(default_factory=list)

    status: MissionStatus = MissionStatus.PENDING

    priority: str = "Medium"

    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MissionResult(BaseModel):
    """
    Final output after one or more executives complete a mission.
    """

    mission_id: str

    success: bool

    summary: str

    executive_results: dict[str, Any] = Field(default_factory=dict)

    recommendations: list[str] = Field(default_factory=list)

    completed_at: datetime = Field(default_factory=datetime.utcnow)