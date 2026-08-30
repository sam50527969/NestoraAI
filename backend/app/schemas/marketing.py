from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


MarketingChannel = Literal[
    "instagram",
    "facebook",
    "linkedin",
    "tiktok",
    "x",
    "email",
    "whatsapp",
    "google_business",
    "google_ads",
]


MarketingPlanStatus = Literal[
    "draft",
    "pending_approval",
    "approved",
    "rejected",
    "running",
    "completed",
    "archived",
]


class MarketingBusinessProfile(BaseModel):
    business_id: str = Field(
        ...,
        min_length=1,
        description="Unique business identifier.",
    )

    business_name: str = Field(
        ...,
        min_length=1,
    )

    industry: str = Field(
        ...,
        min_length=1,
    )

    location: str | None = None

    description: str | None = None

    products_or_services: list[str] = Field(
        default_factory=list,
    )

    target_audience: list[str] = Field(
        default_factory=list,
    )

    differentiators: list[str] = Field(
        default_factory=list,
    )

    current_channels: list[MarketingChannel] = Field(
        default_factory=list,
    )

    preferred_languages: list[str] = Field(
        default_factory=lambda: ["English"],
    )

    brand_voice: str | None = None


class MarketingGoal(BaseModel):
    objective: str = Field(
        ...,
        min_length=3,
        description=(
            "The business outcome the Marketing Director "
            "should help achieve."
        ),
    )

    timeline_days: int = Field(
        default=30,
        ge=1,
        le=365,
    )

    monthly_budget: float = Field(
        default=0,
        ge=0,
    )

    currency: str = Field(
        ...,
        min_length=3,
        max_length=3,
    )

    preferred_channels: list[MarketingChannel] = Field(
        default_factory=list,
    )

    approval_required: bool = True


class MarketingDirectorRequest(BaseModel):
    business: MarketingBusinessProfile

    goal: MarketingGoal

    additional_instructions: str | None = None


class MarketingBusinessAnalysis(BaseModel):
    business_summary: str

    audience_summary: str

    strengths: list[str] = Field(
        default_factory=list,
    )

    weaknesses: list[str] = Field(
        default_factory=list,
    )

    opportunities: list[str] = Field(
        default_factory=list,
    )

    risks: list[str] = Field(
        default_factory=list,
    )

    recommended_positioning: str

    confidence: float = Field(
        default=0.75,
        ge=0,
        le=1,
    )


class MarketingChannelStrategy(BaseModel):
    channel: MarketingChannel

    objective: str

    rationale: str

    content_types: list[str] = Field(
        default_factory=list,
    )

    posting_frequency: str

    budget_percentage: float = Field(
        ge=0,
        le=100,
    )

    expected_leads: int = Field(
        default=0,
        ge=0,
    )


class MarketingStrategy(BaseModel):
    strategy_name: str

    executive_summary: str

    primary_objective: str

    target_segments: list[str] = Field(
        default_factory=list,
    )

    key_messages: list[str] = Field(
        default_factory=list,
    )

    channels: list[MarketingChannelStrategy] = Field(
        default_factory=list,
    )

    success_metrics: list[str] = Field(
        default_factory=list,
    )

    risks: list[str] = Field(
        default_factory=list,
    )

    confidence: float = Field(
        default=0.75,
        ge=0,
        le=1,
    )


class MarketingBudgetItem(BaseModel):
    channel: MarketingChannel

    amount: float = Field(
        ge=0,
    )

    percentage: float = Field(
        ge=0,
        le=100,
    )

    rationale: str


class MarketingBudgetPlan(BaseModel):
    total_budget: float = Field(
        ge=0,
    )

    currency: str

    allocations: list[MarketingBudgetItem] = Field(
        default_factory=list,
    )

    reserve_amount: float = Field(
        default=0,
        ge=0,
    )

    notes: list[str] = Field(
        default_factory=list,
    )


class MarketingContentItem(BaseModel):
    channel: MarketingChannel

    title: str

    content: str

    call_to_action: str

    suggested_publish_time: str | None = None

    hashtags: list[str] = Field(
        default_factory=list,
    )


class MarketingCampaignWeek(BaseModel):
    week_number: int = Field(
        ge=1,
        le=53,
    )

    theme: str

    objective: str

    activities: list[str] = Field(
        default_factory=list,
    )

    content: list[MarketingContentItem] = Field(
        default_factory=list,
    )


class MarketingCampaignPlan(BaseModel):
    campaign_name: str

    duration_days: int = Field(
        ge=1,
        le=365,
    )

    campaign_objective: str

    weeks: list[MarketingCampaignWeek] = Field(
        default_factory=list,
    )

    approval_required: bool = True

    status: Literal[
        "draft",
        "pending_approval",
        "approved",
        "rejected",
        "running",
        "completed",
    ] = "draft"


class MarketingPrediction(BaseModel):
    estimated_reach: int = Field(
        default=0,
        ge=0,
    )

    estimated_engagements: int = Field(
        default=0,
        ge=0,
    )

    estimated_leads: int = Field(
        default=0,
        ge=0,
    )

    estimated_conversions: int = Field(
        default=0,
        ge=0,
    )

    estimated_revenue: float = Field(
        default=0,
        ge=0,
    )

    estimated_roi_percentage: float = 0

    confidence: float = Field(
        default=0.65,
        ge=0,
        le=1,
    )

    assumptions: list[str] = Field(
        default_factory=list,
    )


class MarketingDirectorResponse(BaseModel):
    business_id: str

    analysis: MarketingBusinessAnalysis

    strategy: MarketingStrategy

    budget: MarketingBudgetPlan

    campaign: MarketingCampaignPlan

    prediction: MarketingPrediction

    memory_entries_created: int = Field(
        default=0,
        ge=0,
    )

    approval_required: bool = True


class MarketingPlanSummary(BaseModel):
    id: int

    plan_uid: str

    business_id: str

    business_name: str

    industry: str

    location: str | None = None

    objective: str

    status: MarketingPlanStatus

    approval_required: bool

    approved_by: str | None = None

    approved_at: datetime | None = None

    currency: str

    monthly_budget: float

    timeline_days: int

    memory_entries_created: int = 0

    created_at: datetime

    updated_at: datetime


class MarketingPlanDetail(MarketingPlanSummary):
    request: MarketingDirectorRequest

    response: MarketingDirectorResponse

    analysis: MarketingBusinessAnalysis | None = None

    strategy: MarketingStrategy | None = None

    budget: MarketingBudgetPlan | None = None

    campaign: MarketingCampaignPlan | None = None

    prediction: MarketingPrediction | None = None


class MarketingPlanApprovalRequest(BaseModel):
    approved_by: str = Field(
        ...,
        min_length=1,
        max_length=120,
    )


class MarketingPlanListResponse(BaseModel):
    items: list[MarketingPlanSummary] = Field(
        default_factory=list,
    )

    count: int = Field(
        default=0,
        ge=0,
    )

    limit: int = Field(
        default=50,
        ge=1,
    )

    offset: int = Field(
        default=0,
        ge=0,
    )