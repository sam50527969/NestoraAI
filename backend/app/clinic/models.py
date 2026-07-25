from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
)
from datetime import datetime

from app.database.database import Base


class ClinicLead(Base):
    __tablename__ = "clinic_leads"

    id = Column(Integer, primary_key=True, index=True)

    patient_name = Column(String(200), nullable=False)

    phone = Column(String(50), nullable=False)

    treatment = Column(String(150), nullable=False)

    source = Column(String(100), default="WhatsApp")

    status = Column(String(50), default="New")

    assigned_to = Column(String(100), default="Reception")

    next_followup = Column(DateTime, nullable=True)

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)