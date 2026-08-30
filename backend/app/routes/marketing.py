from __future__ import annotations

import asyncio
import uuid
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.business.access import get_current_business_uid
from app.database.database import get_db
from app.repositories import MarketingPlanRepository
from app.schemas.marketing import (
    MarketingDirectorRequest,
    MarketingDirectorResponse,
)
from app.services.business_search import search_businesses
from app.services.competitor_enrichment import (
    CompetitorEnrichmentService,
)
from app.services.competitor_intelligence import (
    CompetitorIntelligenceService,
)
from app.services.marketing.director import MarketingDirector
from app.services.strategy_generator import (
    StrategyGeneratorService,
)


router = APIRouter(
    prefix="/marketing",
    tags=["Marketing"],
)


class GrowthStrategyRequest(BaseModel):
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
        default="Increase qualified leads and revenue",
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

    competitor_context: list[
        dict[str, Any]
    ] = Field(
        default_factory=list,
    )

    additional_context: dict[
        str,
        Any,
    ] = Field(
        default_factory=dict,
    )


@router.post(
    "/director",
    response_model=MarketingDirectorResponse,
)
async def run_marketing_director(
    request: MarketingDirectorRequest,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid,
    ),
) -> MarketingDirectorResponse:
    if request.business.business_id != business_uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Marketing business context does not match "
                "the active workspace."
            ),
        )

    mission_id = str(uuid.uuid4())

    director = MarketingDirector(
        db=db,
        mission_id=mission_id,
        request=request,
    )

    try:
        context = await director.execute()
        response = director.build_response(context)

        repository = MarketingPlanRepository(db)

        repository.create(
            request_data=request.model_dump(
                mode="json",
            ),
            response_data=response.model_dump(
                mode="json",
            ),
        )

        return response

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Marketing Director execution failed: "
                f"{exc}"
            ),
        ) from exc


async def _enrich_competitor_safely(
    service: CompetitorEnrichmentService,
    competitor: dict[str, Any],
) -> dict[str, Any]:
    try:
        return await asyncio.wait_for(
            service.enrich(competitor),
            timeout=25,
        )

    except Exception as exc:
        print(
            "Competitor enrichment failed: "
            f"{competitor.get('businessName')} | {exc}"
        )

        return {
            **competitor,
            "enrichment_status": "failed",
            "enrichment_confidence": 0,
            "enrichment_sources": [],
            "enrichment_error": str(exc),
        }


def _has_public_value(
    value: Any,
) -> bool:
    invalid_values = {
        "",
        "not found",
        "missing",
        "website missing",
        "phone missing",
        "email missing",
        "none",
        "null",
        "undefined",
        "n/a",
    }

    cleaned = str(
        value or ""
    ).strip().lower()

    return bool(
        cleaned
        and cleaned not in invalid_values
    )


def _refresh_availability_flags(
    competitor: dict[str, Any],
) -> None:
    competitor["websiteAvailable"] = (
        _has_public_value(
            competitor.get("website")
        )
    )

    competitor["phoneAvailable"] = (
        _has_public_value(
            competitor.get("phone")
        )
    )

    competitor["emailAvailable"] = (
        _has_public_value(
            competitor.get("email")
        )
    )


@router.get(
    "/competitors",
    response_model=list[dict[str, Any]],
)
async def discover_competitors(
    category: str = Query(
        ...,
        min_length=1,
    ),
    location: str = Query(
        default="",
        min_length=1,
    ),
    limit: int = Query(
        default=8,
        ge=1,
        le=20,
    ),
    enrich: bool = Query(
        default=True,
    ),
    analyze: bool = Query(
        default=True,
    ),
) -> list[dict[str, Any]]:
    normalized_category = (
        category
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
    )

    category_mapping = {
        "medical center": "clinic",
        "medical centre": "clinic",
        "healthcare": "clinic",
        "dental clinic": "dentist",
        "coffee shop": "cafe",
        "fast food": "restaurant",
    }

    search_category = category_mapping.get(
        normalized_category,
        normalized_category,
    )

    try:
        competitors = await search_businesses(
            business_type=search_category,
            location=location.strip(),
            limit=limit,
        )

        competitors = competitors[:limit]

        if not competitors:
            return []

        if enrich:
            enrichment_service = (
                CompetitorEnrichmentService()
            )

            competitors = await asyncio.gather(
                *[
                    _enrich_competitor_safely(
                        enrichment_service,
                        competitor,
                    )
                    for competitor in competitors
                ]
            )

        for competitor in competitors:
            _refresh_availability_flags(
                competitor
            )

        if analyze:
            intelligence_service = (
                CompetitorIntelligenceService()
            )

            for competitor in competitors:
                try:
                    report = (
                        intelligence_service
                        .analyze(
                            competitor
                        )
                    )

                    competitor[
                        "competitor_intelligence"
                    ] = report.to_dict()

                    competitor[
                        "profileStrength"
                    ] = report.strength.score

                    competitor[
                        "profileStrengthLabel"
                    ] = report.strength.label

                    competitor[
                        "marketPosition"
                    ] = report.market_position

                    competitor[
                        "digitalMaturity"
                    ] = report.digital_maturity

                    competitor[
                        "intelligenceConfidence"
                    ] = report.confidence

                except Exception as exc:
                    competitor[
                        "competitor_intelligence"
                    ] = None

                    competitor[
                        "intelligence_error"
                    ] = str(exc)

        return competitors

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Competitor discovery failed: "
                f"{exc}"
            ),
        ) from exc


@router.post(
    "/strategy",
    response_model=dict[str, Any],
)
async def generate_growth_strategy(
    request: GrowthStrategyRequest,
) -> dict[str, Any]:
    """
    Generate a complete growth strategy from business
    context and optional competitor intelligence.
    """

    service = StrategyGeneratorService()

    try:
        report = service.generate(
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
            competitor_context=(
                request.competitor_context
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
                "Growth strategy generation failed: "
                f"{exc}"
            ),
        ) from exc
