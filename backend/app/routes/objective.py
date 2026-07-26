from __future__ import annotations

from fastapi import APIRouter

from app.schemas.objective import (
    ObjectiveRequest,
    ObjectiveResponse,
    OpportunityResponse,
    StrategyResponse,
)

router = APIRouter(
    prefix="/ceo",
    tags=["AI CEO"],
)


@router.post(
    "/objective",
    response_model=ObjectiveResponse,
)
def analyze_objective(
    request: ObjectiveRequest,
):
    """
    Temporary endpoint.

    In the next package this endpoint will call
    ObjectiveService and BusinessRepository.

    For now we return a fixed response so we can
    verify the API contract end-to-end.
    """

    return ObjectiveResponse(
        success=True,
        opportunities=[
            OpportunityResponse(
                title="Recover inactive customers",
                description="Recover inactive customers before acquiring new ones.",
                estimated_value=25000,
                confidence=0.94,
                executives=[
                    "Marketing",
                    "Follow-up",
                    "Reception",
                ],
            )
        ],
        strategy=StrategyResponse(
            title="Business Growth Strategy",
            summary="Execute the identified opportunities in priority order.",
            confidence=0.94,
            estimated_roi=2.5,
            missions=[
                "Recover inactive customers",
            ],
            executives=[
                "Marketing",
                "Follow-up",
                "Reception",
            ],
            risks=[],
        ),
    )