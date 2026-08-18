from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.models import Lead
from app.schemas.dashboard import (
    DashboardKpis,
    DashboardPipelineStage,
    DashboardSummary,
)


PIPELINE_STAGES = [
    "New",
    "Contacted",
    "Qualified",
    "Proposal",
    "Won",
    "Lost",
]

LOST_STATUS = "Lost"


def normalized_text(
    value: object,
) -> str:
    return str(
        value or ""
    ).strip()


def safe_non_negative_integer(
    value: object,
) -> int:
    try:
        number = int(
            float(value)
        )
    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return 0

    return max(number, 0)


def calculate_ai_score(
    leads: list[Lead],
) -> int:
    scores = [
        safe_non_negative_integer(
            lead.ai_score
        )
        for lead in leads
        if lead.ai_score is not None
    ]

    scores = [
        min(score, 100)
        for score in scores
    ]

    if not scores:
        return 0

    return round(
        sum(scores) / len(scores)
    )


def get_dashboard_summary(
    db: Session,
) -> DashboardSummary:
    leads = db.query(Lead).all()

    total_leads = len(leads)

    high_priority_leads = sum(
        1
        for lead in leads
        if normalized_text(
            lead.priority
        ).lower() == "high"
    )

    qualified_leads = sum(
        1
        for lead in leads
        if normalized_text(
            lead.status
        ).lower() == "qualified"
    )

    won_leads = sum(
        1
        for lead in leads
        if normalized_text(
            lead.status
        ).lower() == "won"
    )

    pipeline_value = sum(
        safe_non_negative_integer(
            lead.estimated_value
        )
        for lead in leads
        if normalized_text(
            lead.status
        ).lower()
        != LOST_STATUS.lower()
    )

    pipeline = [
        DashboardPipelineStage(
            label=stage,
            value=sum(
                1
                for lead in leads
                if normalized_text(
                    lead.status
                ).lower()
                == stage.lower()
            ),
        )
        for stage in PIPELINE_STAGES
    ]

    ai_score = calculate_ai_score(
        leads
    )

    return DashboardSummary(
        kpis=DashboardKpis(
            total_leads=total_leads,
            high_priority_leads=(
                high_priority_leads
            ),
            qualified_leads=(
                qualified_leads
            ),
            won_leads=won_leads,
            pipeline_value=(
                pipeline_value
            ),
            ai_score=ai_score,
        ),
        ai_brief=[
            (
                f"You currently have "
                f"{total_leads} total leads "
                "in your CRM."
            ),
            (
                f"{high_priority_leads} leads "
                "are marked as high priority."
            ),
            (
                f"{qualified_leads} leads are "
                "qualified and ready for "
                "deeper follow-up."
            ),
            (
                "Focus today on high-priority "
                "leads that are still marked "
                "as New."
            ),
        ],
        tasks=[
            (
                "Review all high-priority "
                "leads"
            ),
            (
                "Move contacted leads into "
                "the correct pipeline stage"
            ),
            (
                "Generate outreach for the "
                "top opportunities"
            ),
            (
                "Schedule follow-ups for "
                "qualified leads"
            ),
        ],
        pipeline=pipeline,
        activity=[
            (
                "Dashboard loaded live CRM "
                "statistics"
            ),
            (
                "Pipeline summary calculated "
                "from saved leads"
            ),
            (
                "AI brief generated from CRM "
                "data"
            ),
            "Sales priorities updated",
        ],
    )