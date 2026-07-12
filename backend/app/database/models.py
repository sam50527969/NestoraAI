from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.database.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=True, index=True)
    address = Column(Text, nullable=True)
    phone = Column(String, nullable=True)
    website = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    source = Column(String, nullable=True, default="OpenStreetMap")
    source_id = Column(String, nullable=True, index=True)

    status = Column(String, nullable=False, default="New", index=True)
    priority = Column(String, nullable=False, default="Medium", index=True)
    notes = Column(Text, nullable=True)
    tags = Column(String, nullable=True)
    assigned_to = Column(String, nullable=True)
    last_contacted = Column(String, nullable=True)
    next_follow_up = Column(String, nullable=True)

    ai_score = Column(Integer, nullable=True)
    ai_recommendation = Column(Text, nullable=True)
    ai_opportunity = Column(Text, nullable=True)
    ai_strengths = Column(Text, nullable=True)
    ai_weaknesses = Column(Text, nullable=True)
    ai_analyzed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )