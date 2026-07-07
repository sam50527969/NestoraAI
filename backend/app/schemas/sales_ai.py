from pydantic import BaseModel


class SalesLeadInput(BaseModel):
    name: str
    category: str | None = None
    phone: str | None = None
    website: str | None = None
    priority: str | None = None
    notes: str | None = None


class SalesAnalysisRequest(BaseModel):
    lead: SalesLeadInput


class SalesAnalysisResponse(BaseModel):
    score: int
    strengths: list[str]
    weaknesses: list[str]
    recommendation: str