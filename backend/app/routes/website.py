from __future__ import annotations

from typing import Any

from fastapi import (
    APIRouter,
    HTTPException,
)

from app.schemas.website import (
    WebsiteRequest,
    WebsiteResponse,
)
from app.services.website_analyzer import (
    analyze_website,
)
from app.services.website_intelligence import (
    WebsiteIntelligenceService,
)


router = APIRouter(
    prefix="/website",
    tags=["Website Intelligence"],
)


@router.post(
    "/analyze",
    response_model=WebsiteResponse,
)
def analyze(
    request: WebsiteRequest,
) -> WebsiteResponse:
    """
    Run the existing lightweight website analysis.
    """

    return analyze_website(
        request.url
    )


@router.post(
    "/intelligence",
    response_model=dict[str, Any],
)
async def analyze_website_intelligence(
    request: WebsiteRequest,
) -> dict[str, Any]:
    """
    Run the new Website Intelligence Engine.

    This endpoint crawls the website and extracts
    contact details, social profiles, SEO metadata,
    response time, HTTPS status, and business content.
    """

    service = WebsiteIntelligenceService()

    try:
        profile = await service.analyze(
            website=request.url,
        )

        return profile.to_dict()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Website Intelligence analysis failed: "
                f"{exc}"
            ),
        ) from exc