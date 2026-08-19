import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
)

from app.database.database import (
    Base,
    utc_now,
)


def generate_user_uid() -> str:
    return (
        f"usr_{uuid.uuid4().hex[:16]}"
    )


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_uid = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
        default=generate_user_uid,
    )

    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    full_name = Column(
        String,
        nullable=False,
    )

    password_hash = Column(
        String,
        nullable=False,
    )

    role = Column(
        String,
        nullable=False,
        default="user",
        index=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
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