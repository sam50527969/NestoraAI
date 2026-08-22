from app.executives.ceo.models import (
    ExecutiveAction,
    ExecutivePlan,
    ExecutiveRecommendation,
    PriorityLevel,
    RecommendationStatus,
)
from app.executives.ceo.serialization import (
    deserialize_executive_plan,
    serialize_executive_plan,
)


def build_test_plan() -> ExecutivePlan:
    recommendation = ExecutiveRecommendation(
        title="Increase qualified outreach",
        description=(
            "Focus on high-value qualified leads."
        ),
        department="Sales",
        action_type="sales_growth",
        priority_score=90,
        impact_score=95,
        urgency_score=85,
        confidence_score=88,
        priority_level=PriorityLevel.HIGH,
        status=RecommendationStatus.PENDING,
        estimated_value=50000,
        currency="QAR",
        metadata={
            "source": "ceo_test",
        },
    )

    action = ExecutiveAction(
        title="Prepare sales campaign",
        department="Sales",
        instruction=(
            "Prepare targeted outreach for "
            "high-value qualified leads."
        ),
        recommendation_score=91.5,
        requires_approval=True,
        assigned_worker_id="sales_agent",
        metadata={
            "priority_level": "high",
            "action_type": "sales_growth",
        },
    )

    return ExecutivePlan(
        objective="Increase monthly revenue",
        summary="Prioritize high-value sales opportunities.",
        actions=[action],
        recommendations=[recommendation],
        metadata={
            "company_health": 72,
        },
    )


def test_executive_plan_round_trip():
    original = build_test_plan()

    payload = serialize_executive_plan(
        original
    )

    restored = deserialize_executive_plan(
        payload
    )

    assert restored.objective == original.objective
    assert restored.summary == original.summary
    assert restored.metadata == original.metadata

    assert len(restored.actions) == 1
    assert len(restored.recommendations) == 1

    action = restored.actions[0]

    assert action.title == (
        original.actions[0].title
    )
    assert action.department == "Sales"
    assert action.recommendation_score == 91.5
    assert action.requires_approval is True
    assert action.assigned_worker_id == "sales_agent"
    assert action.metadata["priority_level"] == "high"

    recommendation = (
        restored.recommendations[0]
    )

    assert recommendation.title == (
        original.recommendations[0].title
    )
    assert (
        recommendation.priority_level
        == PriorityLevel.HIGH
    )
    assert (
        recommendation.status
        == RecommendationStatus.PENDING
    )
    assert recommendation.estimated_value == 50000
    assert recommendation.currency == "QAR"


def test_serialized_plan_is_json_safe():
    import json

    plan = build_test_plan()

    payload = serialize_executive_plan(
        plan
    )

    encoded = json.dumps(payload)

    assert encoded
    assert '"priority_level": "high"' in encoded
    assert '"status": "pending"' in encoded