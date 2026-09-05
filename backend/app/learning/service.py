from sqlalchemy.orm import Session

from app.learning.repository import (
    ExecutiveLearningRepository,
)

from app.learning.schemas import (
    ExecutiveLearningContext,
)


class ExecutiveLearningService:

    def __init__(self, db: Session):

        self.repository = (
            ExecutiveLearningRepository(db)
        )

    def build_context(
        self,
        executive: str,
        *,
        business_uid: str,
    ) -> ExecutiveLearningContext:

        memories = (
            self.repository.get_recent_memories(
                executive,
                business_uid=business_uid,
            )
        )

        memory_text = [
            memory.memory
            for memory in memories
        ]

        summary = (
            f"{len(memory_text)} previous memories "
            f"loaded for {executive}."
        )

        return ExecutiveLearningContext(
            executive=executive,
            memories=memory_text,
            summary=summary,
        )