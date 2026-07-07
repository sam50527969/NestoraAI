from fastapi import APIRouter

from app.schemas.website import WebsiteRequest, WebsiteResponse
from app.services.website_analyzer import analyze_website

router = APIRouter(prefix="/website", tags=["Website Intelligence"])


@router.post("/analyze", response_model=WebsiteResponse)
def analyze(request: WebsiteRequest):
    return analyze_website(request.url)