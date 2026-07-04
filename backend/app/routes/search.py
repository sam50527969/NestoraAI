from fastapi import APIRouter, Query

from app.services.business_search import search_businesses

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/businesses")
async def search_for_businesses(
    business_type: str = Query(...),
    location: str = Query(...),
    limit: int = Query(20),
):
    return await search_businesses(business_type, location, limit)