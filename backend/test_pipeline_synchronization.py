from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.database import Base
from app.database.models import Lead
from app.follow_up_activity import service as follow_up_service
from app.follow_up_activity.models import FollowUpActivity
from app.follow_up_activity.schemas import FollowUpOutcomeCreate
from app.pipeline_activity import service as pipeline_service
from app.pipeline_activity.models import PipelineActivity


@pytest.fixture
def test_session_factory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[sessionmaker, None, None]:
    database_path = tmp_path / "nestora-test.db"

    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={
            "check_same_thread": False,
        },
    )

    session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr(
        follow_up_service,
        "SessionLocal",
        session_factory,
    )

    monkeypatch.setattr(
        pipeline_service,
        "SessionLocal",
        session_factory,
    )

    try:
        yield session_factory
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def create_test_lead(
    session_factory: sessionmaker,
    *,
    name: str = "Test Medical Center",
    status: str = "Contacted",
) -> int:
    db: Session = session_factory()

    try:
        lead = Lead(
            name=name,
            category="clinic",
            status=status,
            priority="High",
        )

        db.add(lead)
        db.commit()
        db.refresh(lead)

        return lead.id
    finally:
        db.close()


def test_qualified_follow_up_updates_pipeline_history(
    test_session_factory: sessionmaker,
) -> None:
    lead_id = create_test_lead(
        test_session_factory,
    )

    outcome = FollowUpOutcomeCreate(
        outcome="qualified",
        notes="Lead qualified during test.",
        completed_by="CEO",
    )

    result = (
        follow_up_service
        .record_follow_up_outcome(
            lead_id,
            outcome,
        )
    )

    assert result["lead_id"] == lead_id
    assert result["outcome"] == "qualified"
    assert result["previous_status"] == "Contacted"
    assert result["new_status"] == "Qualified"

    db: Session = test_session_factory()

    try:
        lead = db.get(Lead, lead_id)

        pipeline_activity = (
            db.query(PipelineActivity)
            .filter(
                PipelineActivity.lead_id
                == lead_id
            )
            .one()
        )

        follow_up_activity = (
            db.query(FollowUpActivity)
            .filter(
                FollowUpActivity.lead_id
                == lead_id
            )
            .one()
        )

        assert lead is not None
        assert lead.status == "Qualified"
        assert lead.last_contacted is not None

        assert (
            follow_up_activity.outcome
            == "qualified"
        )

        assert (
            pipeline_activity.previous_status
            == "Contacted"
        )

        assert (
            pipeline_activity.new_status
            == "Qualified"
        )

        assert (
            pipeline_activity.changed_by
            == "CEO"
        )

        assert (
            pipeline_activity.source
            == "CRM Follow-up"
        )

        assert (
            pipeline_activity.notes
            == "Lead qualified during test."
        )
    finally:
        db.close()


def test_won_follow_up_creates_pipeline_history(
    test_session_factory: sessionmaker,
) -> None:
    lead_id = create_test_lead(
        test_session_factory,
        name="Winning Test Lead",
        status="Qualified",
    )

    outcome = FollowUpOutcomeCreate(
        outcome="won",
        notes="Contract signed.",
        completed_by="CEO",
    )

    result = (
        follow_up_service
        .record_follow_up_outcome(
            lead_id,
            outcome,
        )
    )

    assert result["previous_status"] == "Qualified"
    assert result["new_status"] == "Won"
    assert result["next_follow_up"] is None

    db: Session = test_session_factory()

    try:
        lead = db.get(Lead, lead_id)

        pipeline_activity = (
            db.query(PipelineActivity)
            .filter(
                PipelineActivity.lead_id
                == lead_id
            )
            .one()
        )

        assert lead is not None
        assert lead.status == "Won"
        assert lead.next_follow_up is None

        assert (
            pipeline_activity.previous_status
            == "Qualified"
        )

        assert (
            pipeline_activity.new_status
            == "Won"
        )

        assert (
            pipeline_activity.source
            == "CRM Follow-up"
        )
    finally:
        db.close()


def test_rescheduled_follow_up_does_not_create_stage_change(
    test_session_factory: sessionmaker,
) -> None:
    lead_id = create_test_lead(
        test_session_factory,
    )

    next_follow_up = (
        "2026-08-20T09:00:00"
    )

    outcome = FollowUpOutcomeCreate(
        outcome="rescheduled",
        notes="Client requested another date.",
        next_follow_up=next_follow_up,
        completed_by="CEO",
    )

    result = (
        follow_up_service
        .record_follow_up_outcome(
            lead_id,
            outcome,
        )
    )

    assert result["outcome"] == "rescheduled"
    assert result["previous_status"] == "Contacted"
    assert result["new_status"] == "Contacted"
    assert (
        result["next_follow_up"]
        == next_follow_up
    )

    db: Session = test_session_factory()

    try:
        lead = db.get(Lead, lead_id)

        pipeline_count = (
            db.query(PipelineActivity)
            .filter(
                PipelineActivity.lead_id
                == lead_id
            )
            .count()
        )

        follow_up_count = (
            db.query(FollowUpActivity)
            .filter(
                FollowUpActivity.lead_id
                == lead_id
            )
            .count()
        )

        assert lead is not None
        assert lead.status == "Contacted"
        assert (
            lead.next_follow_up
            == next_follow_up
        )

        assert pipeline_count == 0
        assert follow_up_count == 1
    finally:
        db.close()