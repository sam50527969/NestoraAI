from fastapi import APIRouter, Depends

from app.agents.ceo_advisor import build_ceo_brief
from app.business.access import get_current_business_uid


router = APIRouter(
    prefix="/ceo-advisor",
    tags=["CEO Advisor"],
)


@router.get("/brief")
def get_ceo_brief(
    business_uid: str = Depends(
        get_current_business_uid
    ),
):
    return build_ceo_brief(
        business_uid=business_uid
    )