from sqlalchemy.orm import Session

from app.database.models import Lead
from app.schemas.dashboard import DashboardKpis, DashboardPipelineStage, DashboardSummary


PIPELINE_STAGES = ["New", "Contacted", "Qualified", "Proposal", "Won", "Lost"]


def get_dashboard_summary(db: Session) -> DashboardSummary:
    leads = db.query(Lead).all()

    total_leads = len(leads)
    high_priority_leads = len([lead for lead in leads if lead.priority == "High"])
    qualified_leads = len([lead for lead in leads if lead.status == "Qualified"])
    won_leads = len([lead for lead in leads if lead.status == "Won"])

    pipeline_value = (
        high_priority_leads * 1500
        + qualified_leads * 1000
        + won_leads * 2500
    )

    pipeline = [
        DashboardPipelineStage(
            label=stage,
            value=len([lead for lead in leads if lead.status == stage]),
        )
        for stage in PIPELINE_STAGES
    ]

    ai_score = 87 if total_leads > 0 else 0

    return DashboardSummary(
        kpis=DashboardKpis(
            total_leads=total_leads,
            high_priority_leads=high_priority_leads,
            qualified_leads=qualified_leads,
            won_leads=won_leads,
            pipeline_value=pipeline_value,
            ai_score=ai_score,
        ),
        ai_brief=[
            f"You currently have {total_leads} total leads in your CRM.",
            f"{high_priority_leads} leads are marked as high priority.",
            f"{qualified_leads} leads are qualified and ready for deeper follow-up.",
            "Focus today on high-priority leads that are still marked as New.",
        ],
        tasks=[
            "Review all high-priority leads",
            "Move contacted leads into the correct pipeline stage",
            "Generate outreach for the top opportunities",
            "Schedule follow-ups for qualified leads",
        ],
        pipeline=pipeline,
        activity=[
            "Dashboard loaded live CRM statistics",
            "Pipeline summary calculated from saved leads",
            "AI brief generated from CRM data",
            "Sales priorities updated",
        ],
    )