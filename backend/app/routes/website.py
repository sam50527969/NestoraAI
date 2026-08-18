from __future__ import annotations

import logging
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


logger = logging.getLogger(__name__)


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
    result = analyze_website(
        request.url
    )

    return WebsiteResponse(
        **result
    )


@router.post(
    "/intelligence",
    response_model=dict[str, Any],
)
async def analyze_website_intelligence(
    request: WebsiteRequest,
) -> dict[str, Any]:
    service = WebsiteIntelligenceService()

    try:
        profile = await service.analyze(
            website=request.url,
        )
    except Exception as exc:
        logger.exception(
            "Website intelligence analysis failed."
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Website intelligence analysis "
                "could not be completed."
            ),
        ) from exc

    return profile.to_dict()