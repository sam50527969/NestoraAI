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


def generate_activity_uid() -> str:
    return (
        f"out_{uuid.uuid4().hex[:12]}"
    )


class OutreachActivity(Base):
    __tablename__ = "outreach_activities"

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
        default=generate_activity_uid,
    )

    approval_uid = Column(
        String,
        nullable=False,
        index=True,
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

    status = Column(
        String,
        nullable=False,
        default="prepared",
        index=True,
    )

    prepared_by = Column(
        String,
        nullable=False,
        default="CEO Agent",
    )

    phone = Column(
        String,
        nullable=True,
    )

    website = Column(
        String,
        nullable=True,
    )

    email_subject = Column(
        Text,
        nullable=True,
    )

    email_body = Column(
        Text,
        nullable=True,
    )

    whatsapp_message = Column(
        Text,
        nullable=True,
    )

    cold_call_script = Column(
        Text,
        nullable=True,
    )

    proposal_summary = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=utc_now,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    sent_at = Column(
        DateTime,
        nullable=True,
    )