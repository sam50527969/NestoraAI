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


def generate_follow_up_uid() -> str:
    return f"fup_{uuid.uuid4().hex[:12]}"


class FollowUpActivity(Base):
    __tablename__ = "follow_up_activities"

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
        default=generate_follow_up_uid,
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

    outcome = Column(
        String,
        nullable=False,
        index=True,
    )

    notes = Column(
        Text,
        nullable=True,
    )

    previous_status = Column(
        String,
        nullable=True,
    )

    new_status = Column(
        String,
        nullable=True,
    )

    previous_follow_up = Column(
        String,
        nullable=True,
    )

    next_follow_up = Column(
        String,
        nullable=True,
    )

    completed_by = Column(
        String,
        nullable=False,
        default="CEO",
    )

    created_at = Column(
        DateTime,
        default=utc_now,
        nullable=False,
        index=True,
    )