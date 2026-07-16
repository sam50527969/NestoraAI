from fastapi import APIRouter

from app.agents.ceo_advisor import build_ceo_brief


router = APIRouter(
    prefix="/ceo-advisor",
    tags=["CEO Advisor"],
)


@router.get("/brief")
def get_ceo_brief():
    return build_ceo_brief()