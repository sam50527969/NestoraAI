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
    builder = CEOCompanyStateBuilder(db)

    builder._mission_repository.list_all = Mock(
        return_value=[
            make_mission(status="running", progress=50),
            make_mission(status="completed", progress=100),
            make_mission(status="failed", progress=20),
        ]
    )

    state = builder.build()

    assert state.crm is not None
    assert state.missions is not None

    assert state.crm.metrics["total_leads"] == 10
    assert state.crm.metrics["pipeline_value"] == 50000

    assert state.missions.metrics["total"] == 3
    assert state.missions.metrics["running"] == 1
    assert state.missions.metrics["completed"] == 1
    assert state.missions.metrics["failed"] == 1

    assert state.metadata["source"] == "live_nestora_data"
    assert state.metadata["departments_loaded"] == [
        "CRM",
        "Missions",
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
    builder = CEOCompanyStateBuilder(db)

    builder._mission_repository.list_all = Mock(
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
    builder = CEOCompanyStateBuilder(db)

    builder._mission_repository.list_all = Mock(
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
    builder = CEOCompanyStateBuilder(db)

    builder._mission_repository.list_all = Mock(
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
        "75000 QAR"
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