from unittest.mock import Mock, patch

from app.executives.ceo.state_builder import CEOCompanyStateBuilder
from app.schemas.dashboard import (
    DashboardKpis,
    DashboardSummary,
)


def make_dashboard(
    *,
    total_leads: int = 10,
    high_priority_leads: int = 3,
    qualified_leads: int = 4,
    won_leads: int = 2,
    pipeline_value: int = 50000,
    ai_score: int = 80,
) -> DashboardSummary:
    return DashboardSummary(
        kpis=DashboardKpis(
            total_leads=total_leads,
            high_priority_leads=high_priority_leads,
            qualified_leads=qualified_leads,
            won_leads=won_leads,
            pipeline_value=pipeline_value,
            ai_score=ai_score,
        ),
        ai_brief=[],
        tasks=[],
        pipeline=[],
        activity=[],
    )


def make_mission(
    *,
    status: str,
    progress: int,
):
    mission = Mock()
    mission.status = status
    mission.progress = progress
    return mission


@patch(
    "app.executives.ceo.state_builder.get_dashboard_summary"
)
def test_builder_uses_live_crm_and_mission_data(
    mock_dashboard,
):
    mock_dashboard.return_value = make_dashboard()

    db = Mock()
    builder = CEOCompanyStateBuilder(db, business_uid="biz_atlas")

    business = Mock()
    business.finances.currency = "AED"
    builder._business_repository.get_by_uid = Mock(
        return_value=business
    )

    builder._memory_service.list_memories = Mock(
        return_value=[]
    )

    builder._mission_repository.list_by_business = Mock(
        return_value=[
            make_mission(status="running", progress=50),
            make_mission(status="completed", progress=100),
            make_mission(status="failed", progress=20),
        ]
    )

    state = builder.build()

    mock_dashboard.assert_called_once_with(
        db,
        business_uid="biz_atlas",
    )

    builder._mission_repository.list_by_business.assert_called_once_with(
        "biz_atlas",
        limit=100,
    )

    assert state.crm is not None
    assert state.missions is not None

    assert state.crm.metrics["total_leads"] == 10
    assert state.crm.metrics["pipeline_value"] == 50000
    assert state.metadata["business_uid"] == "biz_atlas"
    assert state.metadata["currency"] == "AED"
    assert (
        "Current CRM pipeline value is 50000 AED."
        in state.crm.opportunities
    )

    assert state.missions.metrics["total"] == 3
    assert state.missions.metrics["running"] == 1
    assert state.missions.metrics["completed"] == 1
    assert state.missions.metrics["failed"] == 1

    assert state.metadata["source"] == "live_nestora_data"
    assert state.metadata["departments_loaded"] == [
        "CRM",
        "Missions",
        "Memory",
    ]


@patch(
    "app.executives.ceo.state_builder.get_dashboard_summary"
)
def test_builder_detects_empty_crm_risk(
    mock_dashboard,
):
    mock_dashboard.return_value = make_dashboard(
        total_leads=0,
        high_priority_leads=0,
        qualified_leads=0,
        won_leads=0,
        pipeline_value=0,
        ai_score=0,
    )

    db = Mock()
    builder = CEOCompanyStateBuilder(db, business_uid="biz_atlas")

    business = Mock()
    business.finances.currency = "AED"
    builder._business_repository.get_by_uid = Mock(
        return_value=business
    )

    builder._memory_service.list_memories = Mock(
        return_value=[]
    )

    builder._mission_repository.list_by_business = Mock(
        return_value=[]
    )

    state = builder.build()

    assert state.crm is not None
    assert state.crm.health_score == 20.0
    assert state.crm.status == "critical"
    assert "CRM has no active leads." in state.crm.risks
    assert "CRM has no active leads." in state.critical_risks


@patch(
    "app.executives.ceo.state_builder.get_dashboard_summary"
)
def test_builder_detects_mission_failure(
    mock_dashboard,
):
    mock_dashboard.return_value = make_dashboard()

    db = Mock()
    builder = CEOCompanyStateBuilder(db, business_uid="biz_atlas")

    business = Mock()
    business.finances.currency = "AED"
    builder._business_repository.get_by_uid = Mock(
        return_value=business
    )

    builder._memory_service.list_memories = Mock(
        return_value=[]
    )

    builder._mission_repository.list_by_business = Mock(
        return_value=[
            make_mission(status="failed", progress=25),
        ]
    )

    state = builder.build()

    assert state.missions is not None
    assert state.missions.metrics["failed"] == 1
    assert (
        "1 mission(s) have failed and require review."
        in state.missions.risks
    )


@patch(
    "app.executives.ceo.state_builder.get_dashboard_summary"
)
def test_builder_collects_business_opportunities(
    mock_dashboard,
):
    mock_dashboard.return_value = make_dashboard(
        high_priority_leads=4,
        pipeline_value=75000,
    )

    db = Mock()
    builder = CEOCompanyStateBuilder(db, business_uid="biz_atlas")

    business = Mock()
    business.finances.currency = "AED"
    builder._business_repository.get_by_uid = Mock(
        return_value=business
    )

    builder._memory_service.list_memories = Mock(
        return_value=[]
    )

    builder._mission_repository.list_by_business = Mock(
        return_value=[
            make_mission(status="running", progress=40),
        ]
    )

    state = builder.build()

    assert any(
        "4 high-priority lead(s)"
        in opportunity
        for opportunity in state.major_opportunities
    )

    assert any(
        "75000 AED"
        in opportunity
        for opportunity in state.major_opportunities
    )

    assert any(
        "currently running"
        in opportunity
        for opportunity in state.major_opportunities
    )


def test_health_status_boundaries():
    assert CEOCompanyStateBuilder._health_status(75) == "healthy"
    assert CEOCompanyStateBuilder._health_status(74.99) == "warning"
    assert CEOCompanyStateBuilder._health_status(40) == "warning"
    assert CEOCompanyStateBuilder._health_status(39.99) == "critical"


def make_memory(
    *,
    category: str = "strategy",
    memory: str = "Prioritize qualified healthcare leads.",
    importance: int = 9,
):
    record = Mock()
    record.category = category
    record.memory = memory
    record.importance = importance
    return record


@patch(
    "app.executives.ceo.state_builder.get_dashboard_summary"
)
def test_builder_loads_ceo_executive_memory(
    mock_dashboard,
):
    mock_dashboard.return_value = make_dashboard()

    db = Mock()
    builder = CEOCompanyStateBuilder(db, business_uid="biz_atlas")

    business = Mock()
    business.finances.currency = "AED"
    builder._business_repository.get_by_uid = Mock(
        return_value=business
    )

    builder._mission_repository.list_by_business = Mock(
        return_value=[]
    )
    builder._memory_service.list_memories = Mock(
        return_value=[
            make_memory(),
            make_memory(
                category="sales",
                memory="Follow up high-value leads first.",
                importance=8,
            ),
        ]
    )

    state = builder.build()

    assert state.memory is not None
    assert state.memory.department == "Memory"
    assert state.memory.metrics["total"] == 2
    assert state.memory.metrics["high_importance"] == 2

    assert any(
        "Prioritize qualified healthcare leads."
        in opportunity
        for opportunity in state.memory.opportunities
    )

    builder._memory_service.list_memories.assert_called_once_with(
        executive="CEO",
        limit=10,
    )

    assert "Memory" in state.metadata["departments_loaded"]


@patch(
    "app.executives.ceo.state_builder.get_dashboard_summary"
)
def test_ceo_memory_becomes_decision_context(
    mock_dashboard,
):
    mock_dashboard.return_value = make_dashboard(
        high_priority_leads=0,
        pipeline_value=0,
    )

    db = Mock()
    builder = CEOCompanyStateBuilder(db, business_uid="biz_atlas")

    business = Mock()
    business.finances.currency = "AED"
    builder._business_repository.get_by_uid = Mock(
        return_value=business
    )

    builder._mission_repository.list_by_business = Mock(
        return_value=[]
    )
    builder._memory_service.list_memories = Mock(
        return_value=[
            make_memory(
                category="strategy",
                memory=(
                    "Previous campaign showed healthcare "
                    "leads convert strongly."
                ),
                importance=10,
            )
        ]
    )

    state = builder.build()

    from app.executives.ceo import CEOBrain

    plan = CEOBrain().evaluate(
        company_state=state,
        objective="Choose the next growth priority",
    )

    assert any(
        (
            "Previous campaign showed healthcare "
            "leads convert strongly."
        )
        in recommendation.description
        for recommendation in plan.recommendations
    )


@patch(
    "app.executives.ceo.state_builder.get_dashboard_summary"
)
def test_builder_handles_empty_ceo_memory(
    mock_dashboard,
):
    mock_dashboard.return_value = make_dashboard()

    db = Mock()
    builder = CEOCompanyStateBuilder(db, business_uid="biz_atlas")

    business = Mock()
    business.finances.currency = "AED"
    builder._business_repository.get_by_uid = Mock(
        return_value=business
    )

    builder._mission_repository.list_by_business = Mock(
        return_value=[]
    )
    builder._memory_service.list_memories = Mock(
        return_value=[]
    )

    state = builder.build()

    assert state.memory is not None
    assert state.memory.metrics["total"] == 0
    assert state.memory.opportunities == []
    assert state.memory.health_score == 100.0
