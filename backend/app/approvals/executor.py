import json
import unicodedata
from datetime import datetime
from typing import Any

from app.approvals.models import CEOApproval
from app.approvals.service import (
    parse_payload,
    serialize_approval,
)
from app.database.database import SessionLocal
from app.database.models import Lead
from app.schemas.outreach import (
    OutreachLead,
    OutreachRequest,
)
from app.services.outreach_service import (
    generate_outreach,
)


INVALID_LEAD_NAMES = {
    "",
    "unknown",
    "unknown business",
    "unnamed business",
    "not found",
}

MOJIBAKE_MARKERS = (
    "Ã",
    "Â",
    "Ø",
    "Ù",
    "�",
)


def normalize_name(value: Any) -> str:
    return " ".join(
        str(value or "")
        .strip()
        .lower()
        .split()
    )


def contains_invalid_characters(
    value: str,
) -> bool:
    for character in value:
        if character.isspace():
            continue

        code_point = ord(character)
        category = unicodedata.category(
            character
        )

        if category.startswith("C"):
            return True

        if 0x0080 <= code_point <= 0x00FF:
            return True

    return False


def is_usable_lead_name(
    value: Any,
) -> bool:
    name = str(value or "").strip()
    normalized_name = normalize_name(name)

    if (
        not name
        or normalized_name
        in INVALID_LEAD_NAMES
    ):
        return False

    if any(
        marker in name
        for marker in MOJIBAKE_MARKERS
    ):
        return False

    if contains_invalid_characters(name):
        return False

    return True


def get_priority_rank(
    priority: Any,
) -> int:
    ranks = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1,
    }

    normalized_priority = normalize_name(
        priority
    )

    return ranks.get(
        normalized_priority,
        0,
    )


def should_replace_lead(
    existing_lead: Lead,
    current_lead: Lead,
) -> bool:
    existing_rank = get_priority_rank(
        existing_lead.priority
    )

    current_rank = get_priority_rank(
        current_lead.priority
    )

    if current_rank != existing_rank:
        return (
            current_rank
            > existing_rank
        )

    existing_score = (
        existing_lead.ai_score or 0
    )

    current_score = (
        current_lead.ai_score or 0
    )

    if current_score != existing_score:
        return (
            current_score
            > existing_score
        )

    existing_value = (
        existing_lead.estimated_value or 0
    )

    current_value = (
        current_lead.estimated_value or 0
    )

    return (
        current_value
        > existing_value
    )


def get_unique_priority_leads(
    leads: list[Lead],
) -> list[Lead]:
    unique_leads: dict[str, Lead] = {}

    for lead in leads:
        if not is_usable_lead_name(
            lead.name
        ):
            continue

        if get_priority_rank(
            lead.priority
        ) < 3:
            continue

        normalized_name = normalize_name(
            lead.name
        )

        existing_lead = unique_leads.get(
            normalized_name
        )

        if (
            existing_lead is None
            or should_replace_lead(
                existing_lead,
                lead,
            )
        ):
            unique_leads[
                normalized_name
            ] = lead

    qualified_leads = list(
        unique_leads.values()
    )

    qualified_leads.sort(
        key=lambda lead: (
            get_priority_rank(
                lead.priority
            ),
            lead.ai_score or 0,
            lead.estimated_value or 0,
        ),
        reverse=True,
    )

    return qualified_leads


def build_crm_outreach_action(
    db,
    payload: dict[str, Any],
) -> dict[str, Any]:
    requested_count = int(
        payload.get(
            "high_priority_count",
            5,
        )
        or 5
    )

    target_count = max(
        1,
        min(requested_count, 25),
    )

    all_leads = db.query(Lead).all()

    selected_leads = (
        get_unique_priority_leads(
            all_leads
        )[:target_count]
    )

    outreach_packages = []

    for lead in selected_leads:
        lead_name = str(
            lead.name
        ).strip()

        request = OutreachRequest(
            lead=OutreachLead(
                name=lead_name,
                category=lead.category,
                phone=lead.phone,
                website=lead.website,
                priority=lead.priority,
                notes=lead.notes,
            ),
            offer=(
                payload.get("offer")
                or "starter business package"
            ),
        )

        outreach = generate_outreach(
            request
        )

        outreach_packages.append(
            {
                "lead_id": lead.id,
                "lead_name": lead_name,
                "phone": lead.phone,
                "website": lead.website,
                "priority": lead.priority,
                "score": (
                    lead.ai_score or 0
                ),
                "estimated_value": (
                    lead.estimated_value
                    or 0
                ),
                "email_subject": (
                    outreach.email_subject
                ),
                "email_body": (
                    outreach.email_body
                ),
                "whatsapp_message": (
                    outreach.whatsapp_message
                ),
                "cold_call_script": (
                    outreach.cold_call_script
                ),
                "proposal_summary": (
                    outreach.proposal_summary
                ),
            }
        )

    prepared_count = len(
        outreach_packages
    )

    return {
        "action_type": "crm_outreach",
        "status": "prepared",
        "requested_count": target_count,
        "prepared_count": prepared_count,
        "outreach_packages": (
            outreach_packages
        ),
        "message": (
            "Prepared outreach assets for "
            f"{prepared_count} unique "
            "high-priority CRM "
            f"{'lead' if prepared_count == 1 else 'leads'}."
        ),
    }


def execute_action(
    decision_type: str,
    db,
    payload: dict[str, Any],
) -> dict[str, Any]:
    normalized_type = normalize_name(
        decision_type
    ).replace(" ", "_")

    handlers = {
        "crm_outreach": (
            build_crm_outreach_action
        ),
    }

    handler = handlers.get(
        normalized_type
    )

    if handler is None:
        raise ValueError(
            "No approved-action executor "
            "is registered for "
            f"'{normalized_type}'."
        )

    return handler(
        db,
        payload,
    )


def execute_approval(
    approval_uid: str,
) -> dict[str, Any]:
    db = SessionLocal()

    try:
        approval = (
            db.query(CEOApproval)
            .filter(
                CEOApproval.approval_uid
                == approval_uid
            )
            .first()
        )

        if approval is None:
            raise LookupError(
                "Approval request was not found."
            )

        if approval.status != "approved":
            raise ValueError(
                "Only approved requests can "
                "be executed."
            )

        payload = (
            parse_payload(
                approval.payload_json
            )
            or {}
        )

        execution_result = execute_action(
            approval.decision_type,
            db,
            payload,
        )

        payload[
            "execution_result"
        ] = execution_result

        approval.payload_json = json.dumps(
            payload,
            ensure_ascii=False,
            default=str,
        )

        approval.status = "executed"
        approval.executed_at = (
            datetime.utcnow()
        )

        db.commit()
        db.refresh(approval)

        return serialize_approval(
            approval
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()