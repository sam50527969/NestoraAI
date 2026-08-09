from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


CollaborationStatus = Literal[
    "open",
    "in_progress",
    "awaiting_approval",
    "approved",
    "rejected",
    "completed",
    "cancelled",
]

ContributionType = Literal[
    "recommendation",
    "question",
    "response",
    "analysis",
    "approval",
    "rejection",
    "decision",
    "handoff",
]


class CollaborationSessionCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )

    objective: str = Field(
        min_length=1,
    )

    mission_uid: str | None = Field(
        default=None,
        max_length=64,
    )

    owner: str = Field(
        default="CEO",
        min_length=1,
        max_length=100,
    )

    participants: list[str] = Field(
        default_factory=list,
    )

    shared_context: dict[str, Any] = Field(
        default_factory=dict,
    )


class CollaborationContributionCreate(BaseModel):
    executive: str = Field(
        min_length=1,
        max_length=100,
    )

    contribution_type: ContributionType = (
        "recommendation"
    )

    content: str = Field(
        min_length=1,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class CollaborationDecisionCreate(BaseModel):
    executive: str = Field(
        default="CEO",
        min_length=1,
        max_length=100,
    )

    decision: str = Field(
        min_length=1,
    )

    status: Literal[
        "approved",
        "rejected",
        "completed",
    ] = "approved"

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class CollaborationSessionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    session_uid: str
    mission_uid: str | None
    title: str
    objective: str
    owner: str
    status: str
    participants: list[str]
    shared_context: dict[str, Any]
    final_decision: str | None
    created_at: datetime
    updated_at: datetime | None = None
    closed_at: datetime | None = None


class CollaborationContributionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    contribution_uid: str
    session_uid: str
    executive: str
    contribution_type: str
    content: str
    metadata: dict[str, Any]
    created_at: datetime


class CollaborationSessionDetailResponse(BaseModel):
    session: CollaborationSessionResponse
    contribution_count: int
    contributions: list[
        CollaborationContributionResponse
    ]


class CollaborationSessionListResponse(BaseModel):
    count: int
    sessions: list[CollaborationSessionResponse]
