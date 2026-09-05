from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base
from app.memory.models import ExecutiveMemory
from app.memory.repository import ExecutiveMemoryRepository
from app.memory.schemas import ExecutiveMemoryCreate
from app.memory.service import ExecutiveMemoryService


def make_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    return session_factory()


def test_executive_memory_is_scoped_to_business():
    db = make_db()

    try:
        service = ExecutiveMemoryService(db)

        atlas = service.create_memory(
            ExecutiveMemoryCreate(
                executive="CEO",
                category="strategy",
                memory="Atlas-only memory",
                importance=9,
                source="test",
            ),
            business_uid="biz_atlas",
        )

        dental = service.create_memory(
            ExecutiveMemoryCreate(
                executive="CEO",
                category="strategy",
                memory="Dental-only memory",
                importance=8,
                source="test",
            ),
            business_uid="biz_dental",
        )

        legacy = ExecutiveMemory(
            business_uid=None,
            executive="CEO",
            category="legacy",
            memory="Legacy unowned memory",
            importance=10,
            source="test",
        )

        db.add(legacy)
        db.commit()
        db.refresh(legacy)

        atlas_memories = service.list_memories(
            business_uid="biz_atlas",
            executive="CEO",
        )

        assert [item.id for item in atlas_memories] == [
            atlas.id
        ]

        assert dental.id not in {
            item.id for item in atlas_memories
        }

        assert legacy.id not in {
            item.id for item in atlas_memories
        }

        assert (
            service.get_memory(
                atlas.id,
                business_uid="biz_atlas",
            )
            is not None
        )

        assert (
            service.get_memory(
                dental.id,
                business_uid="biz_atlas",
            )
            is None
        )

        assert (
            service.get_memory(
                legacy.id,
                business_uid="biz_atlas",
            )
            is None
        )

        assert (
            service.delete_memory(
                dental.id,
                business_uid="biz_atlas",
            )
            is False
        )

        assert (
            service.delete_memory(
                legacy.id,
                business_uid="biz_atlas",
            )
            is False
        )

        assert (
            db.query(ExecutiveMemory)
            .filter(ExecutiveMemory.id == dental.id)
            .first()
            is not None
        )

        assert (
            db.query(ExecutiveMemory)
            .filter(ExecutiveMemory.id == legacy.id)
            .first()
            is not None
        )

    finally:
        db.close()


def test_learning_repository_is_scoped_to_business():
    from app.learning.repository import (
        ExecutiveLearningRepository,
    )

    db = make_db()

    try:
        db.add_all(
            [
                ExecutiveMemory(
                    business_uid="biz_atlas",
                    executive="CEO",
                    category="learning",
                    memory="Atlas learning",
                    importance=8,
                    source="test",
                ),
                ExecutiveMemory(
                    business_uid="biz_dental",
                    executive="CEO",
                    category="learning",
                    memory="Dental learning",
                    importance=8,
                    source="test",
                ),
                ExecutiveMemory(
                    business_uid=None,
                    executive="CEO",
                    category="learning",
                    memory="Legacy learning",
                    importance=8,
                    source="test",
                ),
            ]
        )
        db.commit()

        repository = ExecutiveLearningRepository(db)

        memories = repository.get_recent_memories(
            "CEO",
            business_uid="biz_atlas",
        )

        assert [item.memory for item in memories] == [
            "Atlas learning"
        ]

    finally:
        db.close()
