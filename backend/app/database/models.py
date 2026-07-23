import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)

from app.database.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String,
        nullable=False,
        index=True,
    )

    category = Column(
        String,
        nullable=True,
        index=True,
    )

    address = Column(
        Text,
        nullable=True,
    )

    phone = Column(
        String,
        nullable=True,
    )

    website = Column(
        String,
        nullable=True,
    )

    latitude = Column(
        Float,
        nullable=True,
    )

    longitude = Column(
        Float,
        nullable=True,
    )

    source = Column(
        String,
        nullable=True,
        default="OpenStreetMap",
    )

    source_id = Column(
        String,
        nullable=True,
        index=True,
    )

    status = Column(
        String,
        nullable=False,
        default="New",
        index=True,
    )

    priority = Column(
        String,
        nullable=False,
        default="Medium",
        index=True,
    )

    notes = Column(
        Text,
        nullable=True,
    )

    tags = Column(
        String,
        nullable=True,
    )

    assigned_to = Column(
        String,
        nullable=True,
    )

    last_contacted = Column(
        String,
        nullable=True,
    )

    next_follow_up = Column(
        String,
        nullable=True,
    )

    ai_score = Column(
        Integer,
        nullable=True,
    )

    ai_recommendation = Column(
        Text,
        nullable=True,
    )

    ai_opportunity = Column(
        Text,
        nullable=True,
    )

    ai_strengths = Column(
        Text,
        nullable=True,
    )

    ai_weaknesses = Column(
        Text,
        nullable=True,
    )

    ai_analyzed_at = Column(
        DateTime,
        nullable=True,
    )

    opportunity_score = Column(
        Integer,
        nullable=True,
    )

    estimated_value = Column(
        Integer,
        nullable=True,
    )

    closing_probability = Column(
        Integer,
        nullable=True,
    )

    business_potential = Column(
        String,
        nullable=True,
    )

    opportunity_recommendation = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    task_uid = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid.uuid4()),
    )

    mission_id = Column(
        String,
        nullable=False,
        index=True,
    )

    agent_name = Column(
        String,
        nullable=False,
        index=True,
    )

    task_type = Column(
        String,
        nullable=False,
        index=True,
    )

    title = Column(
        String,
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    status = Column(
        String,
        nullable=False,
        default="pending",
        index=True,
    )

    priority = Column(
        String,
        nullable=False,
        default="medium",
        index=True,
    )

    progress = Column(
        Integer,
        nullable=False,
        default=0,
    )

    sequence_number = Column(
        Integer,
        nullable=False,
        default=0,
        index=True,
    )

    depends_on_task_uid = Column(
        String,
        nullable=True,
        index=True,
    )

    input_data = Column(
        Text,
        nullable=True,
    )

    output_data = Column(
        Text,
        nullable=True,
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    retry_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    max_retries = Column(
        Integer,
        nullable=False,
        default=3,
    )

    estimated_value = Column(
        Float,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    started_at = Column(
        DateTime,
        nullable=True,
    )

    completed_at = Column(
        DateTime,
        nullable=True,
    )


class MarketingPlan(Base):
    __tablename__ = "marketing_plans"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    plan_uid = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid.uuid4()),
    )

    business_id = Column(
        String,
        nullable=False,
        index=True,
    )

    business_name = Column(
        String,
        nullable=False,
        index=True,
    )

    industry = Column(
        String,
        nullable=False,
        index=True,
    )

    location = Column(
        String,
        nullable=True,
        index=True,
    )

    objective = Column(
        Text,
        nullable=False,
    )

    status = Column(
        String,
        nullable=False,
        default="draft",
        index=True,
    )

    approval_required = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    approved_by = Column(
        String,
        nullable=True,
    )

    approved_at = Column(
        DateTime,
        nullable=True,
    )

    currency = Column(
        String,
        nullable=False,
        default="QAR",
    )

    monthly_budget = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    timeline_days = Column(
        Integer,
        nullable=False,
        default=30,
    )

    request_data = Column(
        Text,
        nullable=False,
    )

    response_data = Column(
        Text,
        nullable=False,
    )

    analysis_data = Column(
        Text,
        nullable=True,
    )

    strategy_data = Column(
        Text,
        nullable=True,
    )

    budget_data = Column(
        Text,
        nullable=True,
    )

    campaign_data = Column(
        Text,
        nullable=True,
    )

    prediction_data = Column(
        Text,
        nullable=True,
    )

    memory_entries_created = Column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )