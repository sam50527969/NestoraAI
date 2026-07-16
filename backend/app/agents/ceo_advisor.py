from app.database.database import SessionLocal
from app.database.models import Lead


INVALID_BUSINESS_NAMES = {
    "",
    "unknown",
    "unknown business",
    "unnamed business",
    "not found",
}


def normalize_name(value):
    return " ".join(
        str(value or "")
        .strip()
        .lower()
        .split()
    )


def is_valid_business_name(value):
    normalized_name = normalize_name(value)

    return normalized_name not in INVALID_BUSINESS_NAMES


def get_priority_rank(priority):
    priority_value = str(priority or "").strip().lower()

    ranks = {
        "high": 3,
        "medium": 2,
        "low": 1,
    }

    return ranks.get(priority_value, 0)


def should_replace_existing(existing_lead, current_lead):
    existing_priority_rank = get_priority_rank(
        existing_lead.priority
    )
    current_priority_rank = get_priority_rank(
        current_lead.priority
    )

    if current_priority_rank > existing_priority_rank:
        return True

    if current_priority_rank < existing_priority_rank:
        return False

    existing_score = existing_lead.ai_score or 0
    current_score = current_lead.ai_score or 0

    return current_score > existing_score


def build_ceo_brief():
    db = SessionLocal()

    try:
        leads = db.query(Lead).all()
        total_records = len(leads)

        valid_leads = [
            lead
            for lead in leads
            if is_valid_business_name(lead.name)
        ]

        if not valid_leads:
            return {
                "summary": "Your CRM is currently empty.",
                "total_records": total_records,
                "unique_leads": 0,
                "high_priority_count": 0,
                "average_score": 0,
                "priority": [],
                "recommendations": [
                    "Run a new mission to discover business opportunities."
                ],
            }

        unique_leads = {}

        for lead in valid_leads:
            normalized_name = normalize_name(lead.name)
            existing_lead = unique_leads.get(normalized_name)

            if existing_lead is None:
                unique_leads[normalized_name] = lead
                continue

            if should_replace_existing(
                existing_lead,
                lead,
            ):
                unique_leads[normalized_name] = lead

        deduplicated_leads = list(unique_leads.values())

        priority_leads = sorted(
            deduplicated_leads,
            key=lambda lead: (
                get_priority_rank(lead.priority),
                lead.ai_score or 0,
            ),
            reverse=True,
        )[:5]

        high_priority_count = sum(
            1
            for lead in deduplicated_leads
            if get_priority_rank(lead.priority) == 3
        )

        scored_leads = [
            lead.ai_score
            for lead in deduplicated_leads
            if lead.ai_score is not None
        ]

        average_score = (
            round(
                sum(scored_leads) / len(scored_leads)
            )
            if scored_leads
            else 0
        )

        recommendations = []

        if len(deduplicated_leads) < 20:
            recommendations.append(
                "Run another mission to discover more businesses."
            )

        if high_priority_count > 0:
            recommendations.append(
                f"Contact the {high_priority_count} high-priority "
                "lead or leads first."
            )
        else:
            recommendations.append(
                "Review the highest-scoring leads and qualify the strongest."
            )

        recommendations.append(
            "Prepare personalized outreach for the top opportunities."
        )

        recommendations.append(
            "Generate proposals for qualified businesses with strong scores."
        )

        return {
            "summary": (
                f"You currently have {total_records} CRM records "
                f"representing {len(deduplicated_leads)} "
                "unique businesses."
            ),
            "total_records": total_records,
            "unique_leads": len(deduplicated_leads),
            "high_priority_count": high_priority_count,
            "average_score": average_score,
            "priority": [
                {
                    "name": str(lead.name).strip(),
                    "priority": (
                        str(lead.priority).strip()
                        if lead.priority
                        else "Medium"
                    ),
                    "score": lead.ai_score or 0,
                }
                for lead in priority_leads
            ],
            "recommendations": recommendations,
        }

    finally:
        db.close()