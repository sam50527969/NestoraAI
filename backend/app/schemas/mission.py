from pydantic import BaseModel


class MissionRequest(BaseModel):
    business_type: str
    location: str
    quantity: int = 20
    analyze_websites: bool = True
    generate_outreach: bool = True


class MissionStatus(BaseModel):
    mission_id: str
    status: str
    progress: int
    current_step: str
    searched: int
    analyzed: int
    outreach_generated: int