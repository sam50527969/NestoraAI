from sqlalchemy.orm import Session

from app.agents.ceo_brain import CEOBrain


def ask_ceo(db: Session, question: str):
    brain = CEOBrain(db)

    answer = brain.think(question)

    return {
        "answer": answer
    }