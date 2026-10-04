from datetime import datetime

from app.agents.ceo_advisor import (
    build_ceo_brief,
)
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.metadata import metadata
import app.agents.ceo_advisor as advisor
from app.database.models import (
    AgentTask,
    Lead,
    Mission,
)


@pytest.fixture
def session_factory(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'ceo.db'}")
    metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    monkeypatch.setattr(advisor, "SessionLocal", factory)
    yield factory
    engine.dispose()


def test_ceo_brief_is_scoped_to_business(session_factory):
    db = session_factory()

    atlas_uid = "test_ceo_atlas"
    dental_uid = "test_ceo_dental"

    atlas_mission_uid = (
        "test_ceo_atlas_mission"
    )
    dental_mission_uid = (
        "test_ceo_dental_mission"
    )

    try:
        # Remove leftovers from an interrupted
        # previous test run.
        db.query(AgentTask).filter(
            AgentTask.mission_id.in_(
                [
                    atlas_mission_uid,
                    dental_mission_uid,
                ]
            )
        ).delete(
            synchronize_session=False
        )

        db.query(Mission).filter(
            Mission.mission_uid.in_(
                [
                    atlas_mission_uid,
                    dental_mission_uid,
                ]
            )
        ).delete(
            synchronize_session=False
        )

        db.query(Lead).filter(
            Lead.business_uid.in_(
                [
                    atlas_uid,
                    dental_uid,
                ]
            )
        ).delete(
            synchronize_session=False
        )

        db.commit()

        atlas_lead = Lead(
            business_uid=atlas_uid,
            name="Atlas Workshop Lead",
            priority="High",
            ai_score=91,
            estimated_value=12000,
        )

        dental_lead = Lead(
            business_uid=dental_uid,
            name="Dental Clinic Lead",
            priority="High",
            ai_score=99,
            estimated_value=50000,
        )

        atlas_mission = Mission(
            mission_uid=atlas_mission_uid,
            business_uid=atlas_uid,
            title="Atlas Growth Mission",
            objective=(
                "Grow workshop revenue."
            ),
            status="completed",
            progress=100,
            estimated_value=25000,
        )

        dental_mission = Mission(
            mission_uid=dental_mission_uid,
            business_uid=dental_uid,
            title="Dental Patient Mission",
            objective=(
                "Grow dental appointments."
            ),
            status="completed",
            progress=100,
            estimated_value=90000,
        )

        db.add_all(
            [
                atlas_lead,
                dental_lead,
                atlas_mission,
                dental_mission,
            ]
        )
        db.flush()

        atlas_task = AgentTask(
            task_uid="test_ceo_atlas_task",
            mission_id=atlas_mission_uid,
            agent_name="CEO",
            task_type="analysis",
            title="Atlas Executive Report",
            status="completed",
            output_data=(
                '{"summary": '
                '"Atlas-only report"}'
            ),
            estimated_value=5000,
            completed_at=datetime.utcnow(),
        )

        dental_task = AgentTask(
            task_uid="test_ceo_dental_task",
            mission_id=dental_mission_uid,
            agent_name="CEO",
            task_type="analysis",
            title="Dental Executive Report",
            status="completed",
            output_data=(
                '{"summary": '
                '"Dental-only report"}'
            ),
            estimated_value=8000,
            completed_at=datetime.utcnow(),
        )

        db.add_all(
            [
                atlas_task,
                dental_task,
            ]
        )
        db.commit()

        brief = build_ceo_brief(
            business_uid=atlas_uid
        )

        assert brief["unique_leads"] == 1

        assert [
            lead["name"]
            for lead in brief["priority"]
        ] == [
            "Atlas Workshop Lead"
        ]

        assert (
            brief["mission_overview"]["total"]
            == 1
        )

        assert (
            brief["mission_overview"][
                "total_estimated_value"
            ]
            == 25000
        )

        reports = brief[
            "executive_reports"
        ]

        assert len(reports) == 1

        assert (
            reports[0]["mission_uid"]
            == atlas_mission_uid
        )

        assert (
            reports[0]["task_title"]
            == "Atlas Executive Report"
        )

        assert (
            reports[0]["summary"]
            == "Atlas-only report"
        )

        serialized = str(brief)

        assert "Dental Clinic Lead" not in serialized
        assert "Dental Patient Mission" not in serialized
        assert "Dental Executive Report" not in serialized
        assert "Dental-only report" not in serialized

    finally:
        db.query(AgentTask).filter(
            AgentTask.mission_id.in_(
                [
                    atlas_mission_uid,
                    dental_mission_uid,
                ]
            )
        ).delete(
            synchronize_session=False
        )

        db.query(Mission).filter(
            Mission.mission_uid.in_(
                [
                    atlas_mission_uid,
                    dental_mission_uid,
                ]
            )
        ).delete(
            synchronize_session=False
        )

        db.query(Lead).filter(
            Lead.business_uid.in_(
                [
                    atlas_uid,
                    dental_uid,
                ]
            )
        ).delete(
            synchronize_session=False
        )

        db.commit()
        db.close()
