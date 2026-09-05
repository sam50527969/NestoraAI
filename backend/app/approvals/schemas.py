from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ApprovalCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=240,
    )

    description: str | None = None

    decision_type: str = (
        "executive_action"
    )

    source_type: str = (
        "executive_report"
    )

    source_uid: str | None = None

    requested_by: str = "CEO Agent"

    payload: dict[str, Any] | None = None


class ApprovalDecision(BaseModel):
    reviewed_by: str = Field(
        default="CEO",
        min_length=1,
        max_length=120,
    )

    decision_note: str | None = None


class ApprovalResponse(BaseModel):
    approval_uid: str
    business_uid: str | None = None
    decision_type: str
    title: str
    description: str | None
    source_type: str
    source_uid: str | None
    status: str
    requested_by: str
    reviewed_by: str | None
    decision_note: str | None
    payload: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime
    reviewed_at: datetime | None
    executed_at: datetime | None