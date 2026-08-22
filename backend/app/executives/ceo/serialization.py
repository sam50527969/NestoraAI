from __future__ import annotations

from typing import Any

from app.executives.ceo.models import (
    ExecutiveAction,
    ExecutivePlan,
    ExecutiveRecommendation,
    PriorityLevel,
    RecommendationStatus,
)


def serialize_executive_plan(
    plan: ExecutivePlan,
) -> dict[str, Any]:
    return {
        "objective": plan.objective,
        "summary": plan.summary,
        "actions": [
            {
                "title": action.title,
                "department": action.department,
                "instruction": action.instruction,
                "recommendation_score": (
                    action.recommendation_score
                ),
                "requires_approval": (
                    action.requires_approval
                ),
                "assigned_worker_id": (
                    action.assigned_worker_id
                ),
                "metadata": dict(
                    action.metadata
                ),
            }
            for action in plan.actions
        ],
        "recommendations": [
            {
                "title": recommendation.title,
                "description": (
                    recommendation.description
                ),
                "department": (
                    recommendation.department
                ),
                "action_type": (
                    recommendation.action_type
                ),
                "priority_score": (
                    recommendation.priority_score
                ),
                "impact_score": (
                    recommendation.impact_score
                ),
                "urgency_score": (
                    recommendation.urgency_score
                ),
                "confidence_score": (
                    recommendation.confidence_score
                ),
                "priority_level": (
                    recommendation
                    .priority_level
                    .value
                ),
                "status": (
                    recommendation.status.value
                ),
                "estimated_value": (
                    recommendation.estimated_value
                ),
                "currency": (
                    recommendation.currency
                ),
                "metadata": dict(
                    recommendation.metadata
                ),
            }
            for recommendation
            in plan.recommendations
        ],
        "metadata": dict(plan.metadata),
    }


def deserialize_executive_plan(
    payload: dict[str, Any],
) -> ExecutivePlan:
    actions = [
        ExecutiveAction(
            title=str(
                item.get("title", "")
            ),
            department=str(
                item.get("department", "")
            ),
            instruction=str(
                item.get("instruction", "")
            ),
            recommendation_score=float(
                item.get(
                    "recommendation_score",
                    0,
                )
            ),
            requires_approval=bool(
                item.get(
                    "requires_approval",
                    True,
                )
            ),
            assigned_worker_id=(
                item.get(
                    "assigned_worker_id"
                )
            ),
            metadata=dict(
                item.get("metadata") or {}
            ),
        )
        for item in payload.get(
            "actions",
            [],
        )
    ]

    recommendations = [
        ExecutiveRecommendation(
            title=str(
                item.get("title", "")
            ),
            description=str(
                item.get(
                    "description",
                    "",
                )
            ),
            department=str(
                item.get(
                    "department",
                    "",
                )
            ),
            action_type=str(
                item.get(
                    "action_type",
                    "",
                )
            ),
            priority_score=float(
                item.get(
                    "priority_score",
                    0,
                )
            ),
            impact_score=float(
                item.get(
                    "impact_score",
                    0,
                )
            ),
            urgency_score=float(
                item.get(
                    "urgency_score",
                    0,
                )
            ),
            confidence_score=float(
                item.get(
                    "confidence_score",
                    0,
                )
            ),
            priority_level=PriorityLevel(
                item.get(
                    "priority_level",
                    PriorityLevel.MEDIUM.value,
                )
            ),
            status=RecommendationStatus(
                item.get(
                    "status",
                    RecommendationStatus.PENDING.value,
                )
            ),
            estimated_value=(
                item.get("estimated_value")
            ),
            currency=str(
                item.get(
                    "currency",
                    "QAR",
                )
            ),
            metadata=dict(
                item.get("metadata") or {}
            ),
        )
        for item in payload.get(
            "recommendations",
            [],
        )
    ]

    return ExecutivePlan(
        objective=str(
            payload.get("objective", "")
        ),
        summary=str(
            payload.get("summary", "")
        ),
        actions=actions,
        recommendations=recommendations,
        metadata=dict(
            payload.get("metadata") or {}
        ),
    )