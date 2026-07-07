from pydantic import BaseModel


class WebsiteRequest(BaseModel):
    url: str


class WebsiteResponse(BaseModel):
    score: int
    strengths: list[str]
    issues: list[str]
    recommendation: str