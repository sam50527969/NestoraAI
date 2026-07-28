from __future__ import annotations

from pydantic import BaseModel, Field


class ObjectiveRequest(BaseModel):
    """
    Request sent by the frontend when asking the AI CEO
    to analyze a business objective.
    """

    business_id: str = Field(
        ...,
        min_length=1,
        examples=["clinic-001"],
    )

    objective: str = Field(
        ...,
        min_length=3,
        max_length=500,
        examples=["Increase monthly revenue"],
    )


class OpportunityResponse(BaseModel):
    """
    Opportunity identified during analysis.
    """

    title: str

    description: str

    estimated_value: float

    confidence: float

    executives: list[str]


class StrategyResponse(BaseModel):
    """
    Strategy returned by the AI CEO.
    """

    title: str

    summary: str

    confidence: float

    estimated_roi: float

    missions: list[str]

    executives: list[str]

    risks: list[str]


class ObjectiveResponse(BaseModel):
    """
    Complete AI CEO response, including the persisted mission
    created from the analyzed objective.
    """

    success: bool

    mission_uid: str

    mission_status: str

    opportunities: list[OpportunityResponse]

    strategy: StrategyResponse