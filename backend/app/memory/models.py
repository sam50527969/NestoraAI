from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.database.database import Base


class ExecutiveMemory(Base):
    __tablename__ = "executive_memory"

    id = Column(Integer, primary_key=True, index=True)

    business_uid = Column(
        String,
        nullable=True,
        index=True,
    )

    executive = Column(String(100), index=True)

    category = Column(String(100), index=True)

    importance = Column(Integer, default=5)

    memory = Column(Text)

    source = Column(String(100), default="mission")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
