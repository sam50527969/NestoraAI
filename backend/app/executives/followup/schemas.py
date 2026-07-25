from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class FollowupRequest(BaseModel):
    lead_name: str = Field(..., min_length=1)
    business_type: str = Field(..., min_length=1)
    service: str = Field(..., min_length=1)
    current_status: str = Field(..., min_length=1)
    days_since_last_contact: int = Field(default=0, ge=0)


class FollowupRecommendation(BaseModel):
    priority: Literal["Low", "Medium", "High", "Urgent"]

    lead_loss_risk: Literal[
        "Low",
        "Medium",
        "High",
        "Critical",
    ]

    next_action: str = Field(..., min_length=1)

    preferred_channel: Literal[
        "WhatsApp",
        "Phone",
        "SMS",
        "Email",
        "In Person",
    ]

    best_time: str = Field(..., min_length=1)

    confidence: int = Field(
        ...,
        ge=0,
        le=100,
    )

    reason: str = Field(..., min_length=1)

    message: str = Field(..., min_length=1)

    @field_validator(
        "next_action",
        "best_time",
        "reason",
        "message",
        mode="before",
    )
    @classmethod
    def strip_text_fields(cls, value: str) -> str:
        if not isinstance(value, str):
            return value

        return value.strip()