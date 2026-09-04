from __future__ import annotations

from typing import Any

from fastapi import (
    APIRouter,
    HTTPException,
)
from pydantic import (
    BaseModel,
    Field,
)

from app.services.business_analysis import (
    BusinessAnalysisService,
)


router = APIRouter(
    prefix="/business-analysis",
    tags=["Business Analysis"],
)


class BusinessAnalysisRequest(BaseModel):
    business_name: str = Field(
        ...,
        min_length=1,
    )

    industry: str = Field(
        ...,
        min_length=1,
    )

    location: str = Field(
        ...,
        min_length=1,
    )

    objective: str = Field(
        default=(
            "Increase qualified leads "
            "and revenue"
        ),
        min_length=1,
    )

    timeline_days: int = Field(
        default=90,
        ge=30,
        le=365,
    )

    monthly_budget: float = Field(
        default=0.0,
        ge=0,
    )

    currency: str = Field(
        ...,
        min_length=1,
    )

    average_sale_value: float = Field(
        default=500.0,
        ge=0,
    )

    competitor_limit: int = Field(
        default=5,
        ge=1,
        le=10,
    )

    additional_context: dict[
        str,
        Any,
    ] = Field(
        default_factory=dict,
    )


@router.post(
    "/analyze",
    response_model=dict[str, Any],
)
async def analyze_business(
    request: BusinessAnalysisRequest,
) -> dict[str, Any]:
    """
    Run Nestora's autonomous business-analysis pipeline.
    """

    service = BusinessAnalysisService()

    try:
        report = await service.analyze(
            business_name=request.business_name,
            industry=request.industry,
            location=request.location,
            objective=request.objective,
            timeline_days=request.timeline_days,
            monthly_budget=request.monthly_budget,
            currency=request.currency,
            average_sale_value=(
                request.average_sale_value
            ),
            competitor_limit=(
                request.competitor_limit
            ),
            additional_context=(
                request.additional_context
            ),
        )

        return report.to_dict()

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Business analysis failed: "
                f"{exc}"
            ),
        ) from exc