import json
from typing import Any

from app.database.database import SessionLocal
from app.database.models import (
    AgentTask,
    Lead,
    Mission,
)


INVALID_BUSINESS_NAMES = {
    "",
    "unknown",
    "unknown business",
    "unnamed business",
    "not found",
}


def normalize_name(value: Any) -> str:
    return " ".join(
        str(value or "")
        .strip()
        .lower()
        .split()
    )


def is_valid_business_name(value: Any) -> bool:
    return (
        normalize_name(value)
        not in INVALID_BUSINESS_NAMES
    )


def get_priority_rank(priority: Any) -> int:
    ranks = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1,
    }

    return ranks.get(
        normalize_name(priority),
        0,
    )


def should_replace_existing(
    existing_lead: Lead,
    current_lead: Lead,
) -> bool:
    existing_priority_rank = (
        get_priority_rank(
            existing_lead.priority,
        )
    )

    current_priority_rank = (
        get_priority_rank(
            current_lead.priority,
        )
    )

    if (
        current_priority_rank
        > existing_priority_rank
    ):
        return True

    if (
        current_priority_rank
        < existing_priority_rank
    ):
        return False

    existing_score = (
        existing_lead.ai_score or 0
    )

    current_score = (
        current_lead.ai_score or 0
    )

    return current_score > existing_score


def parse_json(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(
        value,
        (dict, list, int, float, bool),
    ):
        return value

    if not isinstance(value, str):
        return value

    stripped_value = value.strip()

    if not stripped_value:
        return None

    try:
        return json.loads(stripped_value)
    except (TypeError, ValueError):
        return {
            "result": stripped_value,
        }


def get_report_summary(
    report: Any,
    fallback: str,
) -> str:
    if isinstance(report, str):
        return report

    if not isinstance(report, dict):
        return fallback

    summary_keys = (
        "executive_summary",
        "summary",
        "result",
        "recommendation",
        "recommendations",
        "conclusion",
        "overview",
    )

    for key in summary_keys:
        value = report.get(key)

        if isinstance(value, str):
            value = value.strip()

            if value:
                return value

        if isinstance(value, list) and value:
            first_item = value[0]

            if isinstance(first_item, str):
                return first_item

    nested_output = report.get("output")

    if nested_output is not None:
        return get_report_summary(
            nested_output,
            fallback,
        )

    return fallback


def serialize_datetime(value: Any) -> str | None:
    if value is None:
        return None

    isoformat = getattr(
        value,
        "isoformat",
        None,
    )

    if callable(isoformat):
        return isoformat()

    return str(value)


def build_lead_snapshot(
    leads: list[Lead],
) -> dict[str, Any]:
    total_records = len(leads)

    valid_leads = [
        lead
        for lead in leads
        if is_valid_business_name(
            lead.name,
        )
    ]

    unique_leads: dict[str, Lead] = {}

    for lead in valid_leads:
        normalized_name = normalize_name(
            lead.name,
        )

        existing_lead = unique_leads.get(
            normalized_name,
        )

        if (
            existing_lead is None
            or should_replace_existing(
                existing_lead,
                lead,
            )
        ):
            unique_leads[
                normalized_name
            ] = lead

    deduplicated_leads = list(
        unique_leads.values()
    )

    priority_leads = sorted(
        deduplicated_leads,
        key=lambda lead: (
            get_priority_rank(
                lead.priority,
            ),
            lead.ai_score or 0,
        ),
        reverse=True,
    )[:5]

    high_priority_count = sum(
        1
        for lead in deduplicated_leads
        if get_priority_rank(
            lead.priority,
        )
        >= 3
    )

    scored_leads = [
        lead.ai_score
        for lead in deduplicated_leads
        if lead.ai_score is not None
    ]

    average_score = (
        round(
            sum(scored_leads)
            / len(scored_leads)
        )
        if scored_leads
        else 0
    )

    return {
        "total_records": total_records,
        "unique_leads": len(
            deduplicated_leads
        ),
        "high_priority_count": (
            high_priority_count
        ),
        "average_score": average_score,
        "priority": [
            {
                "name": str(
                    lead.name
                ).strip(),
                "priority": (
                    str(
                        lead.priority
                    ).strip()
                    if lead.priority
                    else "Medium"
                ),
                "status": (
                    str(lead.status).strip()
                    if lead.status
                    else "New"
                ),
                "score": (
                    lead.ai_score or 0
                ),
                "estimated_value": (
                    lead.estimated_value
                    or 0
                ),
                "recommendation": (
                    lead.ai_recommendation
                    or lead.opportunity_recommendation
                ),
            }
            for lead in priority_leads
        ],
    }


def build_mission_snapshot(
    missions: list[Mission],
) -> dict[str, Any]:
    status_counts = {
        "planned": 0,
        "running": 0,
        "completed": 0,
        "failed": 0,
        "paused": 0,
    }

    for mission in missions:
        status = normalize_name(
            mission.status
        )

        if status in status_counts:
            status_counts[status] += 1

    total_estimated_value = sum(
        mission.estimated_value or 0
        for mission in missions
    )

    completed_missions = [
        mission
        for mission in missions
        if normalize_name(
            mission.status
        )
        == "completed"
    ]

    average_progress = (
        round(
            sum(
                mission.progress or 0
                for mission in missions
            )
            / len(missions)
        )
        if missions
        else 0
    )

    return {
        "total": len(missions),
        "planned": status_counts[
            "planned"
        ],
        "running": status_counts[
            "running"
        ],
        "completed": status_counts[
            "completed"
        ],
        "failed": status_counts[
            "failed"
        ],
        "paused": status_counts[
            "paused"
        ],
        "average_progress": (
            average_progress
        ),
        "total_estimated_value": round(
            total_estimated_value,
            2,
        ),
        "recent_completed": [
            {
                "mission_uid": (
                    mission.mission_uid
                ),
                "title": mission.title,
                "objective": (
                    mission.objective
                ),
                "estimated_value": (
                    mission.estimated_value
                    or 0
                ),
                "completed_at": (
                    serialize_datetime(
                        mission.completed_at
                    )
                ),
            }
            for mission in sorted(
                completed_missions,
                key=lambda item: (
                    item.completed_at
                    or item.updated_at
                    or item.created_at
                ),
                reverse=True,
            )[:5]
        ],
    }


def build_executive_reports(
    tasks: list[AgentTask],
    missions: list[Mission],
) -> list[dict[str, Any]]:
    mission_lookup = {
        mission.mission_uid: mission
        for mission in missions
    }

    completed_tasks = [
        task
        for task in tasks
        if normalize_name(
            task.status
        )
        == "completed"
        and task.output_data
    ]

    completed_tasks.sort(
        key=lambda task: (
            task.completed_at
            or task.updated_at
            or task.created_at
        ),
        reverse=True,
    )

    reports = []

    for task in completed_tasks[:8]:
        report = parse_json(
            task.output_data
        )

        mission = mission_lookup.get(
            task.mission_id
        )

        reports.append(
            {
                "task_uid": (
                    task.task_uid
                ),
                "mission_uid": (
                    task.mission_id
                ),
                "mission_title": (
                    mission.title
                    if mission
                    else "Mission"
                ),
                "task_title": (
                    task.title
                ),
                "executive": (
                    task.agent_name
                ),
                "status": task.status,
                "summary": (
                    get_report_summary(
                        report,
                        (
                            "Executive report "
                            "completed."
                        ),
                    )
                ),
                "estimated_value": (
                    task.estimated_value
                    or 0
                ),
                "completed_at": (
                    serialize_datetime(
                        task.completed_at
                    )
                ),
                "report": report,
            }
        )

    return reports


def build_recommendations(
    lead_snapshot: dict[str, Any],
    mission_snapshot: dict[str, Any],
    reports: list[dict[str, Any]],
    tasks: list[AgentTask],
) -> list[str]:
    recommendations = []

    if lead_snapshot["unique_leads"] < 20:
        recommendations.append(
            "Launch a discovery mission to "
            "expand the qualified opportunity "
            "pipeline."
        )

    if (
        lead_snapshot[
            "high_priority_count"
        ]
        > 0
    ):
        recommendations.append(
            "Prioritize personalized outreach "
            f"for the {lead_snapshot['high_priority_count']} "
            "high-priority opportunities."
        )

    failed_tasks = [
        task
        for task in tasks
        if normalize_name(
            task.status
        )
        == "failed"
    ]

    if failed_tasks:
        recommendations.append(
            f"Review and resolve "
            f"{len(failed_tasks)} failed "
            "executive task"
            f"{'' if len(failed_tasks) == 1 else 's'}."
        )

    if mission_snapshot["running"] > 0:
        recommendations.append(
            "Review active mission progress "
            "and unblock any delayed executive "
            "dependencies."
        )

    if reports:
        recommendations.append(
            "Review the latest executive "
            "deliverables and approve the "
            "highest-impact next actions."
        )
    else:
        recommendations.append(
            "Complete an executive mission to "
            "generate decision-ready reports."
        )

    if (
        mission_snapshot[
            "total_estimated_value"
        ]
        > 0
    ):
        recommendations.append(
            "Allocate resources toward missions "
            "with the strongest estimated value "
            "and execution readiness."
        )

    return recommendations[:5]


def build_ceo_brief(
    *,
    business_uid: str,
) -> dict[str, Any]:
    db = SessionLocal()

    try:
        leads = (
            db.query(Lead)
            .filter(
                Lead.business_uid
                == business_uid
            )
            .all()
        )

        missions = (
            db.query(Mission)
            .filter(
                Mission.business_uid
                == business_uid
            )
            .all()
        )

        mission_uids = [
            mission.mission_uid
            for mission in missions
        ]

        tasks = (
            db.query(AgentTask)
            .filter(
                AgentTask.mission_id.in_(
                    mission_uids
                )
            )
            .all()
            if mission_uids
            else []
        )

        lead_snapshot = (
            build_lead_snapshot(leads)
        )

        mission_snapshot = (
            build_mission_snapshot(
                missions
            )
        )

        executive_reports = (
            build_executive_reports(
                tasks,
                missions,
            )
        )

        recommendations = (
            build_recommendations(
                lead_snapshot,
                mission_snapshot,
                executive_reports,
                tasks,
            )
        )

        summary = (
            "Nestora AI is monitoring "
            f"{mission_snapshot['total']} missions, "
            f"{mission_snapshot['running']} active "
            "missions, "
            f"{mission_snapshot['completed']} completed "
            "missions, and "
            f"{lead_snapshot['unique_leads']} unique "
            "CRM opportunities."
        )

        return {
            "summary": summary,
            **lead_snapshot,
            "mission_overview": (
                mission_snapshot
            ),
            "executive_reports": (
                executive_reports
            ),
            "recommendations": (
                recommendations
            ),
            "generated_at": (
                serialize_datetime(
                    __import__(
                        "datetime"
                    ).datetime.utcnow()
                )
            ),
        }

    finally:
        db.close()