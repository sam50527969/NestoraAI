from pydantic import BaseModel


class AgentStartRequest(BaseModel):
    business_type: str
    location: str
    quantity: int = 20
    analyze_websites: bool = True
    generate_outreach: bool = True


class AgentResult(BaseModel):
    searched: int
    analyzed: int
    outreach_generated: int
    leads: list