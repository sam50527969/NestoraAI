from pydantic import BaseModel, Field


class FollowupMessage(BaseModel):
    day: int = Field(description="Day in the follow-up sequence.")
    channel: str = Field(description="Communication channel.")
    subject: str = Field(description="Subject or headline.")
    message: str = Field(description="Customer-facing message.")
    objective: str = Field(description="Purpose of this follow-up.")


class FollowupKPI(BaseModel):
    name: str
    target: str
    measurement_method: str


class FollowupReport(BaseModel):
    executive: str = "Follow-up"

    task_title: str

    status: str = "completed"

    executive_summary: str

    strategy: list[str]

    followup_sequence: list[FollowupMessage]

    recommended_actions: list[str]

    kpis: list[FollowupKPI]

    risks: list[str]