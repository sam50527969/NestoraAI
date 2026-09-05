from __future__ import annotations

from sqlalchemy.orm import Session

from app.memory.models import ExecutiveMemory


class ExecutiveMemoryRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        *,
        business_uid: str,
        executive: str,
        category: str,
        memory: str,
        importance: int = 5,
        source: str = "mission",
    ) -> ExecutiveMemory:
        record = ExecutiveMemory(
            business_uid=business_uid,
            executive=executive,
            category=category,
            memory=memory,
            importance=importance,
            source=source,
        )

        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)

        return record

    def list_by_executive(
        self,
        executive: str,
        *,
        business_uid: str,
        limit: int = 50,
    ) -> list[ExecutiveMemory]:
        return (
            self._db.query(ExecutiveMemory)
            .filter(
                ExecutiveMemory.business_uid == business_uid,
                ExecutiveMemory.executive == executive,
            )
            .order_by(
                ExecutiveMemory.importance.desc(),
                ExecutiveMemory.created_at.desc(),
            )
            .limit(limit)
            .all()
        )

    def list_all(
        self,
        *,
        business_uid: str,
        limit: int = 100,
    ) -> list[ExecutiveMemory]:
        return (
            self._db.query(ExecutiveMemory)
            .filter(
                ExecutiveMemory.business_uid == business_uid,
            )
            .order_by(
                ExecutiveMemory.created_at.desc(),
            )
            .limit(limit)
            .all()
        )

    def get_by_id(
        self,
        memory_id: int,
        *,
        business_uid: str,
    ) -> ExecutiveMemory | None:
        return (
            self._db.query(ExecutiveMemory)
            .filter(
                ExecutiveMemory.id == memory_id,
                ExecutiveMemory.business_uid == business_uid,
            )
            .first()
        )

    def delete(
        self,
        memory_id: int,
        *,
        business_uid: str,
    ) -> bool:
        record = self.get_by_id(
            memory_id,
            business_uid=business_uid,
        )

        if record is None:
            return False

        self._db.delete(record)
        self._db.commit()

        return True
