from app.schemas.dashboard import DashboardKpis, DashboardPipelineStage, DashboardSummary


def get_dashboard_summary() -> DashboardSummary:
    return DashboardSummary(
        kpis=DashboardKpis(
            new_leads=23,
            pipeline_value=18500,
            tasks_today=4,
            ai_score=87,
        ),
        ai_brief=[
            "Target restaurants, cafés, gyms, salons and automotive businesses today.",
            "Prioritize businesses with phone numbers and websites.",
            "Focus on Doha first, then expand to Al Wakrah and Lusail.",
            "Recommended offer: 99 QAR starter business package.",
        ],
        tasks=[
            "Find 20 new businesses in Doha",
            "Save qualified leads to CRM",
            "Review high-potential leads",
            "Prepare outreach message",
        ],
        pipeline=[
            DashboardPipelineStage(label="New", value=23),
            DashboardPipelineStage(label="Contacted", value=12),
            DashboardPipelineStage(label="Qualified", value=7),
            DashboardPipelineStage(label="Proposal", value=3),
            DashboardPipelineStage(label="Won", value=1),
        ],
        activity=[
            "CRM dashboard opened",
            "Lead details module enabled",
            "Save Lead workflow completed",
            "Business search connected",
        ],
    )