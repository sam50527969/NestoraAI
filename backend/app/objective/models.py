from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ObjectiveStatus(str, Enum):
    DRAFT = "draft"
    ANALYZING = "analyzing"
    READY = "ready"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(slots=True)
class BusinessObjective:
    """
    High-level business goal submitted by the owner.

    Example:
        Increase clinic revenue by 20%.
    """

    id: str
    title: str
    description: str = ""
    business_id: str | None = None
    created_by: str | None = None
    status: ObjectiveStatus = ObjectiveStatus.DRAFT
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """
        Validate the minimum information required for analysis.
        """

        if not self.id.strip():
            raise ValueError("Objective ID cannot be empty.")

        if not self.title.strip():
            raise ValueError("Objective title cannot be empty.")


@dataclass(slots=True)
class BusinessOpportunity:
    """
    Opportunity identified by the AI CEO during analysis.
    """

    title: str
    description: str
    estimated_value: float = 0.0
    confidence: float = 0.0
    executives: list[str] = field(default_factory=list)
    reasoning: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    required_data: list[str] = field(default_factory=list)

    def validate(self) -> None:
        """
        Validate opportunity fields.
        """

        if not self.title.strip():
            raise ValueError("Opportunity title cannot be empty.")

        if not self.description.strip():
            raise ValueError("Opportunity description cannot be empty.")

        if self.estimated_value < 0:
            raise ValueError(
                "Estimated opportunity value cannot be negative."
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Opportunity confidence must be between 0.0 and 1.0."
            )


@dataclass(slots=True)
class StrategyRecommendation:
    """
    Strategy proposed by the AI CEO.
    """

    title: str
    summary: str
    estimated_roi: float = 0.0
    confidence: float = 0.0
    missions: list[str] = field(default_factory=list)
    executives: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    success_metrics: list[str] = field(default_factory=list)

    def validate(self) -> None:
        """
        Validate strategy recommendation fields.
        """

        if not self.title.strip():
            raise ValueError("Strategy title cannot be empty.")

        if not self.summary.strip():
            raise ValueError("Strategy summary cannot be empty.")

        if self.estimated_roi < 0:
            raise ValueError(
                "Estimated ROI cannot be negative."
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Strategy confidence must be between 0.0 and 1.0."
            )


@dataclass(slots=True)
class ObjectiveAnalysisResult:
    """
    Structured output produced by the Objective Analyzer.

    The Strategist consumes this object to generate a business
    strategy without depending on the internal analyzer logic.
    """

    objective: BusinessObjective
    opportunities: list[BusinessOpportunity] = field(
        default_factory=list,
    )
    missing_information: list[str] = field(
        default_factory=list,
    )
    risks: list[str] = field(
        default_factory=list,
    )
    recommended_executives: list[str] = field(
        default_factory=list,
    )
    relevant_metrics: list[str] = field(
        default_factory=list,
    )
    observations: list[str] = field(
        default_factory=list,
    )
    confidence: float = 0.0
    ready_for_strategy: bool = False
    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    @property
    def opportunity_count(self) -> int:
        return len(self.opportunities)

    @property
    def has_missing_information(self) -> bool:
        return bool(self.missing_information)

    @property
    def has_risks(self) -> bool:
        return bool(self.risks)

    def validate(self) -> None:
        """
        Validate the complete analysis result.
        """

        self.objective.validate()

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Analysis confidence must be between 0.0 and 1.0."
            )

        for opportunity in self.opportunities:
            opportunity.validate()

        if self.ready_for_strategy and not self.opportunities:
            raise ValueError(
                "An analysis cannot be ready for strategy "
                "without at least one opportunity."
            )