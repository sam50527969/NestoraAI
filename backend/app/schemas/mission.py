from pydantic import BaseModel, Field


class MissionRequest(BaseModel):
    business_type: str
    location: str
    quantity: int = 20
    analyze_websites: bool = True
    generate_outreach: bool = True
    minimum_quality: int = Field(default=60, ge=0, le=100)
    priority_filter: str = "all"


class MissionAgentStatus(BaseModel):
    name: str
    role: str
    icon: str
    status: str = "waiting"
    progress: int = Field(default=0, ge=0, le=100)
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
    agents: list[MissionAgentStatus] = Field(default_factory=list)
    activity: list[MissionActivityItem] = Field(default_factory=list)