from __future__ import annotations

from typing import Any

from fastapi import (
    APIRouter,
    Depends,
)
from pydantic import (
    BaseModel,
    Field,
)
from sqlalchemy.orm import Session

from app.agents.ceo_agent import (
    ask_ceo,
    prepare_ceo_plan,
)
from app.business.access import get_current_business_uid
from app.database.database import (
    get_db,
)


router = APIRouter(
    prefix="/ceo",
    tags=["CEO Agent"],
)


class CEOQuestionRequest(BaseModel):
    question: str


class CEOAnswerResponse(BaseModel):
    answer: str


class CEOPlanRequest(BaseModel):
    objective: str = Field(
        min_length=1,
    )

    source_uid: str | None = None


class CEOPlanApprovalResponse(BaseModel):
    approval_uid: str
    title: str
    status: str


class CEOExecutableActionResponse(
    BaseModel
):
    title: str
    department: str
    instruction: str
    recommendation_score: float


class CEOPlanResponse(BaseModel):
    objective: str
    summary: str
    action_count: int
    recommendation_count: int
    approval_count: int
    executable_count: int
    requires_approval: bool

    approvals: list[
        CEOPlanApprovalResponse
    ] = Field(
        default_factory=list
    )

    executable_actions: list[
        CEOExecutableActionResponse
    ] = Field(
        default_factory=list
    )


@router.post(
    "/ask",
    response_model=CEOAnswerResponse,
)
def ask_ceo_question(
    request: CEOQuestionRequest,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid,
    ),
):
    return ask_ceo(
        db=db,
        question=request.question,
        business_uid=business_uid,
    )


@router.post(
    "/plan",
    response_model=CEOPlanResponse,
)
def create_ceo_plan(
    request: CEOPlanRequest,
    db: Session = Depends(get_db),
    business_uid: str = Depends(
        get_current_business_uid,
    ),
) -> dict[str, Any]:
    return prepare_ceo_plan(
        db=db,
        objective=request.objective,
        business_uid=business_uid,
        source_uid=request.source_uid,
    )