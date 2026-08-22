from app.executives.ceo import (
    CEOBrain,
    CompanyState,
    DepartmentState,
)


def build_company_state() -> CompanyState:
    state = CompanyState()

    state.crm = DepartmentState(
        department="CRM",
        status="warning",
        health_score=35,
        summary="Lead pipeline is shrinking.",
        risks=["Only 12 active leads remain."],
        opportunities=["Import 250 new restaurant leads."],
    )

    state.marketing = DepartmentState(
        department="Marketing",
        status="healthy",
        health_score=82,
        summary="Campaign performance improving.",
        opportunities=["Launch new restaurant campaign."],
    )

    state.critical_risks.append(
        "Sales pipeline may run dry within two weeks."
    )

    state.major_opportunities.append(
        "Expand into dental clinic market."
    )

    return state


def test_company_state_calculates_overall_health():
    state = build_company_state()

    score = state.calculate_overall_health()

    assert score == 58.5
    assert state.overall_health_score == 58.5


def test_ceo_brain_creates_ranked_executive_plan():
    state = build_company_state()
    state.calculate_overall_health()

    ceo = CEOBrain()

    plan = ceo.evaluate(
        company_state=state,
        objective="Increase monthly revenue",
    )

    assert plan.objective == "Increase monthly revenue"
    assert plan.actions
    assert plan.recommendations

    scores = [
        recommendation.calculate_final_score()
        for recommendation in plan.recommendations
    ]

    assert scores == sorted(scores, reverse=True)

    assert plan.recommendations[0].action_type == "critical_risk"
    assert plan.recommendations[0].department == "CEO"


def test_ceo_brain_limits_plan_to_five_actions():
    state = build_company_state()

    state.crm.risks.extend(
        [
            "CRM risk two.",
            "CRM risk three.",
            "CRM risk four.",
        ]
    )

    ceo = CEOBrain()
    plan = ceo.evaluate(state)

    assert plan.metadata["total_recommendations_received"] == 9
    assert plan.metadata["actions_created"] == 5
    assert len(plan.recommendations) == 5
    assert len(plan.actions) == 5


def test_ceo_actions_require_approval():
    state = build_company_state()

    ceo = CEOBrain()
    plan = ceo.evaluate(state)

    assert plan.actions
    assert all(action.requires_approval for action in plan.actions)


def test_ceo_brain_handles_empty_company_state():
    state = CompanyState()

    assert state.calculate_overall_health() == 0.0

    ceo = CEOBrain()
    plan = ceo.evaluate(state)

    assert plan.actions == []
    assert plan.recommendations == []
    assert "No immediate executive actions" in plan.summary