from __future__ import annotations

from sqlalchemy.orm import Session

from app.memory.models import ExecutiveMemory
from app.memory.repository import ExecutiveMemoryRepository
from app.memory.schemas import ExecutiveMemoryCreate


class ExecutiveMemoryService:
    def __init__(self, db: Session) -> None:
        self._repository = ExecutiveMemoryRepository(db)

    def create_memory(
        self,
        payload: ExecutiveMemoryCreate,
    ) -> ExecutiveMemory:
        return self._repository.create(
            executive=payload.executive,
            category=payload.category,
            memory=payload.memory,
            importance=payload.importance,
            source=payload.source,
        )

    def list_memories(
        self,
        *,
        executive: str | None = None,
        limit: int = 100,
    ) -> list[ExecutiveMemory]:
        if executive:
            return self._repository.list_by_executive(
                executive,
                limit=limit,
            )

        return self._repository.list_all(
            limit=limit,
        )

    def get_memory(
        self,
        memory_id: int,
    ) -> ExecutiveMemory | None:
        return self._repository.get_by_id(
            memory_id,
        )

    def delete_memory(
        self,
        memory_id: int,
    ) -> bool:
        return self._repository.delete(
            memory_id,
        )