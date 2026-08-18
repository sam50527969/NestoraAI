from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from app.services.business_search import (
    search_businesses,
)


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.get("/businesses")
async def search_for_businesses(
    business_type: str = Query(
        ...,
        min_length=1,
        max_length=160,
    ),
    location: str = Query(
        ...,
        min_length=1,
        max_length=160,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
):
    normalized_business_type = (
        " ".join(
            business_type.strip().split()
        )
    )

    normalized_location = (
        " ".join(
            location.strip().split()
        )
    )

    if not normalized_business_type:
        raise HTTPException(
            status_code=422,
            detail=(
                "Business type must not "
                "be empty."
            ),
        )

    if not normalized_location:
        raise HTTPException(
            status_code=422,
            detail=(
                "Location must not be empty."
            ),
        )

    try:
        return await search_businesses(
            normalized_business_type,
            normalized_location,
            limit,
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=(
                "Business search providers "
                "are temporarily unavailable."
            ),
        ) from error