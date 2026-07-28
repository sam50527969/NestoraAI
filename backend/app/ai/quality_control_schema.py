from pydantic import BaseModel, Field


class ExecutiveReview(BaseModel):
    executive_name: str = Field(
        description="Name of the executive or department being reviewed."
    )

    score: int = Field(
        ge=0,
        le=100,
        description="Quality score between 0 and 100.",
    )

    strengths: list[str] = Field(
        default_factory=list,
        description="Strong aspects of the executive's work.",
    )

    issues: list[str] = Field(
        default_factory=list,
        description="Problems, weaknesses, or missing information.",
    )

    recommendations: list[str] = Field(
        default_factory=list,
        description="Recommended improvements for this executive's work.",
    )


class QualityControlReport(BaseModel):
    executive: str = "Quality Control"

    task_title: str

    status: str = "completed"

    approval_status: str = Field(
        description=(
            "Final approval decision such as Approved, "
            "Approved with Recommendations, or Revision Required."
        )
    )

    overall_score: int = Field(
        ge=0,
        le=100,
        description="Overall mission quality score between 0 and 100.",
    )

    consistency_score: int = Field(
        ge=0,
        le=100,
        description=(
            "Score measuring consistency between all executive outputs."
        ),
    )

    completeness_score: int = Field(
        ge=0,
        le=100,
        description=(
            "Score measuring whether the mission output is complete."
        ),
    )

    executive_summary: str = Field(
        description="Concise summary of the quality-control findings."
    )

    executive_reviews: list[ExecutiveReview] = Field(
        default_factory=list,
        description="Individual reviews of previous executive outputs.",
    )

    contradictions: list[str] = Field(
        default_factory=list,
        description=(
            "Conflicting offers, facts, targets, messages, or instructions."
        ),
    )

    missing_items: list[str] = Field(
        default_factory=list,
        description="Important information missing from the mission output.",
    )

    risks: list[str] = Field(
        default_factory=list,
        description="Risks identified during the review.",
    )

    recommendations: list[str] = Field(
        default_factory=list,
        description="Mission-level recommendations before execution.",
    )

    approved_for_execution: bool = Field(
        description=(
            "True only when the mission output is sufficiently complete, "
            "consistent, practical, and safe for execution."
        ),
    )