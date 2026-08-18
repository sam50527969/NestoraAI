from fastapi import APIRouter

from app.schemas.outreach import (
    OutreachRequest,
    OutreachResponse,
)
from app.services.outreach_service import (
    generate_outreach,
)


router = APIRouter(
    prefix="/outreach",
    tags=["Outreach"],
)


@router.post(
    "/generate",
    response_model=OutreachResponse,
)
def generate_outreach_assets(
    request: OutreachRequest,
):
    return generate_outreach(request)