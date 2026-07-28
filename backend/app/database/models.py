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

class Business(Base):
    __tablename__ = "businesses"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    business_uid = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid.uuid4()),
    )

    name = Column(
        String,
        nullable=False,
        index=True,
    )

    industry = Column(
        String,
        nullable=False,
        index=True,
    )

    country = Column(
        String,
        nullable=False,
        index=True,
    )

    size = Column(
        String,
        nullable=False,
        default="small",
        index=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    currency = Column(
        String,
        nullable=False,
        default="QAR",
    )

    employee_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    departments = Column(
        Text,
        nullable=True,
    )

    roles = Column(
        Text,
        nullable=True,
    )

    total_customers = Column(
        Integer,
        nullable=False,
        default=0,
    )

    active_customers = Column(
        Integer,
        nullable=False,
        default=0,
    )

    inactive_customers = Column(
        Integer,
        nullable=False,
        default=0,
    )

    average_monthly_customers = Column(
        Integer,
        nullable=False,
        default=0,
    )

    returning_customer_rate = Column(
        Float,
        nullable=True,
    )

    average_customer_value = Column(
        Float,
        nullable=True,
    )

    monthly_revenue = Column(
        Float,
        nullable=True,
    )

    monthly_expenses = Column(
        Float,
        nullable=True,
    )

    average_transaction_value = Column(
        Float,
        nullable=True,
    )

    marketing_budget = Column(
        Float,
        nullable=True,
    )

    outstanding_receivables = Column(
        Float,
        nullable=True,
    )

    daily_capacity = Column(
        Integer,
        nullable=True,
    )

    average_daily_volume = Column(
        Integer,
        nullable=True,
    )

    cancellation_rate = Column(
        Float,
        nullable=True,
    )

    utilization_rate = Column(
        Float,
        nullable=True,
    )

    locations_count = Column(
        Integer,
        nullable=False,
        default=1,
    )

    working_hours = Column(
        Text,
        nullable=True,
    )

    goals = Column(
        Text,
        nullable=True,
    )

    metadata_json = Column(
        Text,
        nullable=True,
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

class Mission(Base):
    __tablename__ = "missions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    mission_uid = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
        default=lambda: f"mis_{uuid.uuid4().hex[:12]}",
    )

    business_uid = Column(
        String,
        nullable=False,
        index=True,
    )

    objective_uid = Column(
        String,
        nullable=True,
        index=True,
    )

    title = Column(
        String,
        nullable=False,
        index=True,
    )

    objective = Column(
        Text,
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    status = Column(
        String,
        nullable=False,
        default="planned",
        index=True,
    )

    priority = Column(
        String,
        nullable=False,
        default="medium",
        index=True,
    )

    estimated_value = Column(
        Float,
        nullable=True,
    )

    expected_roi = Column(
        Float,
        nullable=True,
    )

    progress = Column(
        Integer,
        nullable=False,
        default=0,
    )

    strategy_data = Column(
        Text,
        nullable=True,
    )

    metadata_json = Column(
        Text,
        nullable=True,
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

    started_at = Column(
        DateTime,
        nullable=True,
    )

    completed_at = Column(
        DateTime,
        nullable=True,
    )

class MissionEvent(Base):
    __tablename__ = "mission_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    event_uid = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
        default=lambda: f"evt_{uuid.uuid4().hex[:12]}",
    )

    mission_uid = Column(
        String,
        nullable=False,
        index=True,
    )

    executive = Column(
        String,
        nullable=False,
        index=True,
    )

    event_type = Column(
        String,
        nullable=False,
        index=True,
    )

    status = Column(
        String,
        nullable=False,
        default="info",
        index=True,
    )

    message = Column(
        Text,
        nullable=False,
    )

    metadata_json = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
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