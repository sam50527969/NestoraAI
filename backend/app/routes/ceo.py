from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.ceo_agent import ask_ceo
from app.database.database import get_db


router = APIRouter(prefix="/ceo", tags=["CEO Agent"])


class CEOQuestionRequest(BaseModel):
    question: str


class CEOAnswerResponse(BaseModel):
    answer: str


@router.post("/ask", response_model=CEOAnswerResponse)
def ask_ceo_question(
    request: CEOQuestionRequest,
    db: Session = Depends(get_db),
):
    return ask_ceo(
        db=db,
        question=request.question,
    )