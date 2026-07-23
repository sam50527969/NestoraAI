from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.repositories import MarketingPlanRepository
from app.schemas.marketing import (
    MarketingDirectorRequest,
    MarketingDirectorResponse,
)
from app.services.marketing.director import MarketingDirector


router = APIRouter(
    prefix="/marketing",
    tags=["Marketing"],
)


@router.post(
    "/director",
    response_model=MarketingDirectorResponse,
)
async def run_marketing_director(
    request: MarketingDirectorRequest,
    db: Session = Depends(get_db),
) -> MarketingDirectorResponse:
    """
    Execute the complete Marketing Director workflow
    and persist the generated plan.
    """

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