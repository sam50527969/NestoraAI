from sqlalchemy.orm import Session

from app.memory.models import ExecutiveMemory


class ExecutiveLearningRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_recent_memories(
        self,
        executive: str,
        limit: int = 5,
    ):
        return (
            self.db.query(ExecutiveMemory)
            .filter(
                ExecutiveMemory.executive == executive
            )
            .order_by(
                ExecutiveMemory.updated_at.desc()
            )
            .limit(limit)
            .all()
        )