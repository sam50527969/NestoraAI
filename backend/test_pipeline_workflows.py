from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.database import Base
from app.database.models import Lead
from app.outreach_activity import service as outreach_service
from app.outreach_activity.models import OutreachActivity
from app.pipeline_activity.models import PipelineActivity
from app.schemas.crm import LeadUpdate
from app.services import crm_service


@pytest.fixture
def test_session_factory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[sessionmaker, None, None]:
    database_path = (
        tmp_path
        / "nestora-workflows-test.db"
    )

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
        outreach_service,
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
    name: str,
    status: str = "New",
) -> int:
    db: Session = session_factory()

    try:
        lead = Lead(
            name=name,
            category="clinic",
            status=status,
            priority="High",
            business_uid="biz_atlas",
        )

        db.add(lead)
        db.commit()
        db.refresh(lead)

        return lead.id
    finally:
        db.close()


def create_prepared_outreach(
    session_factory: sessionmaker,
    *,
    lead_id: int,
    lead_name: str,
) -> str:
    db: Session = session_factory()

    try:
        activity = OutreachActivity(
            approval_uid=(
                f"approval-test-{lead_id}"
            ),
            lead_id=lead_id,
            lead_name=lead_name,
            status="prepared",
            prepared_by="CEO Agent",
            phone="+97450000000",
            email_subject="Test outreach",
            email_body="Test outreach body",
        )

        db.add(activity)
        db.commit()
        db.refresh(activity)

        return activity.activity_uid
    finally:
        db.close()


def test_manual_stage_change_creates_pipeline_history(
    test_session_factory: sessionmaker,
) -> None:
    lead_id = create_test_lead(
        test_session_factory,
        name="Manual Pipeline Test",
    )

    db: Session = test_session_factory()

    try:
        updated_lead = (
            crm_service.update_lead(
                db,
                lead_id,
                LeadUpdate(
                    status="Contacted",
                ),
                business_uid="biz_atlas",
            )
        )

        assert updated_lead is not None
        assert (
            updated_lead.status
            == "Contacted"
        )

        activity = (
            db.query(PipelineActivity)
            .filter(
                PipelineActivity.lead_id
                == lead_id
            )
            .one()
        )

        assert (
            activity.previous_status
            == "New"
        )

        assert (
            activity.new_status
            == "Contacted"
        )

        assert (
            activity.changed_by
            == "CRM User"
        )

        assert (
            activity.source
            == "CRM Pipeline"
        )
    finally:
        db.close()


def test_same_stage_does_not_create_pipeline_history(
    test_session_factory: sessionmaker,
) -> None:
    lead_id = create_test_lead(
        test_session_factory,
        name="Unchanged Pipeline Test",
        status="Contacted",
    )

    db: Session = test_session_factory()

    try:
        updated_lead = (
            crm_service.update_lead(
                db,
                lead_id,
                LeadUpdate(
                    status="Contacted",
                ),
                business_uid="biz_atlas",
            )
        )

        assert updated_lead is not None
        assert (
            updated_lead.status
            == "Contacted"
        )

        activity_count = (
            db.query(PipelineActivity)
            .filter(
                PipelineActivity.lead_id
                == lead_id
            )
            .count()
        )

        assert activity_count == 0
    finally:
        db.close()


def test_sent_outreach_updates_lead_and_pipeline_history(
    test_session_factory: sessionmaker,
) -> None:
    lead_name = (
        "Sent Outreach Test Clinic"
    )

    lead_id = create_test_lead(
        test_session_factory,
        name=lead_name,
    )

    activity_uid = (
        create_prepared_outreach(
            test_session_factory,
            lead_id=lead_id,
            lead_name=lead_name,
        )
    )

    result = (
        outreach_service
        .mark_outreach_activity_sent(
            activity_uid,
            business_uid="biz_atlas",
        )
    )

    assert (
        result["activity_uid"]
        == activity_uid
    )

    assert result["status"] == "sent"
    assert result["sent_at"] is not None

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
        assert lead.status == "Contacted"
        assert lead.last_contacted is not None
        assert lead.next_follow_up is not None

        assert (
            pipeline_activity.previous_status
            == "New"
        )

        assert (
            pipeline_activity.new_status
            == "Contacted"
        )

        assert (
            pipeline_activity.changed_by
            == "CEO Agent"
        )

        assert (
            pipeline_activity.source
            == "Sent Outreach"
        )

        assert (
            activity_uid
            in pipeline_activity.notes
        )
    finally:
        db.close()


def test_marking_sent_outreach_twice_is_idempotent(
    test_session_factory: sessionmaker,
) -> None:
    lead_name = (
        "Idempotent Outreach Test"
    )

    lead_id = create_test_lead(
        test_session_factory,
        name=lead_name,
    )

    activity_uid = (
        create_prepared_outreach(
            test_session_factory,
            lead_id=lead_id,
            lead_name=lead_name,
        )
    )

    first_result = (
        outreach_service
        .mark_outreach_activity_sent(
            activity_uid,
            business_uid="biz_atlas",
        )
    )

    second_result = (
        outreach_service
        .mark_outreach_activity_sent(
            activity_uid,
            business_uid="biz_atlas",
        )
    )

    assert first_result["status"] == "sent"
    assert second_result["status"] == "sent"

    db: Session = test_session_factory()

    try:
        pipeline_count = (
            db.query(PipelineActivity)
            .filter(
                PipelineActivity.lead_id
                == lead_id
            )
            .count()
        )

        assert pipeline_count == 1
    finally:
        db.close()
