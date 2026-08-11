from datetime import datetime
from typing import Literal

from pydantic import BaseModel


FollowUpOutcome = Literal[
    "contacted",
    "qualified",
    "won",
    "lost",
    "no_response",
    "rescheduled",
]


class FollowUpOutcomeCreate(BaseModel):
    outcome: FollowUpOutcome
    notes: str | None = None
    next_follow_up: str | None = None
    completed_by: str = "CEO"


class FollowUpActivityResponse(BaseModel):
    activity_uid: str
    lead_id: int
    lead_name: str
    outcome: str
    notes: str | None = None
    previous_status: str | None = None
    new_status: str | None = None
    previous_follow_up: str | None = None
    next_follow_up: str | None = None
    completed_by: str
    created_at: datetime