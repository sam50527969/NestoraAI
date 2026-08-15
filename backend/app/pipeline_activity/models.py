import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
)

from app.database.database import (
    Base,
    utc_now,
)


def generate_pipeline_activity_uid() -> str:
    return (
        f"pipe_{uuid.uuid4().hex[:12]}"
    )


class PipelineActivity(Base):
    __tablename__ = "pipeline_activities"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    activity_uid = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
        default=generate_pipeline_activity_uid,
    )

    lead_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    lead_name = Column(
        String,
        nullable=False,
        index=True,
    )

    previous_status = Column(
        String,
        nullable=False,
    )

    new_status = Column(
        String,
        nullable=False,
        index=True,
    )

    changed_by = Column(
        String,
        nullable=False,
        default="CRM User",
    )

    source = Column(
        String,
        nullable=False,
        default="CRM Pipeline",
    )

    notes = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=utc_now,
        nullable=False,
        index=True,
    )