import json
import unicodedata
from typing import Any

from app.approvals.models import CEOApproval
from app.approvals.service import (
    parse_payload,
    serialize_approval,
)
from app.core.execution.execution_service import (
    execution_service,
)
from app.database.database import (
    SessionLocal,
    utc_now,
)
from app.database.models import Lead
from app.executives.ceo.serialization import (
    deserialize_executive_plan,
)
from app.execution_history.service import (
    save_execution_record,
)
from app.outreach_activity.service import (
    save_prepared_outreach,
)
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
    "ÃƒÆ’",
    "Ãƒâ€š",
    "ÃƒËœ",
    "Ãƒâ„¢",
    "Ã¯Â¿Â½",
)


def normalize_name(
    value: Any,
) -> str:
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

        if (
            0x0080
            <= code_point
            <= 0x00FF
        ):
            return True

    return False


def is_usable_lead_name(
    value: Any,
) -> bool:
    name = str(
        value or ""
    ).strip()

    normalized_name = (
        normalize_name(name)
    )

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

    if contains_invalid_characters(
        name
    ):
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

    normalized_priority = (
        normalize_name(priority)
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
        existing_lead.estimated_value
        or 0
    )

    current_value = (
        current_lead.estimated_value
        or 0
    )

    return (
        current_value
        > existing_value
    )


def get_unique_priority_leads(
    leads: list[Lead],
) -> list[Lead]:
    unique_leads: dict[
        str,
        Lead,
    ] = {}

    for lead in leads:
        if not is_usable_lead_name(
            lead.name
        ):
            continue

        if (
            get_priority_rank(
                lead.priority
            )
            < 3
        ):
            continue

        normalized_name = (
            normalize_name(
                lead.name
            )
        )

        existing_lead = (
            unique_leads.get(
                normalized_name
            )
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
    approval_uid: str,
    business_uid: str,
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
        min(
            requested_count,
            25,
        ),
    )

    all_leads = (
        db.query(Lead)
        .filter(
            Lead.business_uid
            == business_uid
        )
        .all()
    )

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
                or (
                    "starter business "
                    "package"
                )
            ),
        )

        outreach = generate_outreach(
            request
        )

        activity = (
            save_prepared_outreach(
                db,
                approval_uid=(
                    approval_uid
                ),
                lead=lead,
                outreach=outreach,
            )
        )

        outreach_packages.append(
            {
                "activity_uid": (
                    activity.activity_uid
                ),
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
                    outreach
                    .whatsapp_message
                ),
                "cold_call_script": (
                    outreach
                    .cold_call_script
                ),
                "proposal_summary": (
                    outreach
                    .proposal_summary
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
            "Prepared and saved outreach "
            f"assets for {prepared_count} "
            "unique high-priority CRM "
            f"{'lead' if prepared_count == 1 else 'leads'}."
        ),
    }


async def execute_executive_action(
    db,
    payload: dict[str, Any],
    approval_uid: str,
    business_uid: str,
) -> dict[str, Any]:
    plan_payload = payload.get(
        "executive_plan"
    )

    if not isinstance(
        plan_payload,
        dict,
    ):
        raise ValueError(
            "Executive action payload must "
            "contain an executive_plan."
        )

    plan = deserialize_executive_plan(
        plan_payload
    )

    result = await (
        execution_service.execute_plan(
            plan,
            business_uid=business_uid,
        )
    )

    execution_result = {
        "action_type": "executive_action",
        "status": (
            "completed"
            if result.success
            else "failed"
        ),
        "success": result.success,
        "mission_id": (
            result.mission.id
        ),
        "mission_title": (
            result.mission.title
        ),
        "workflow_id": (
            result.workflow.id
        ),
        "completed_task_count": (
            result.completed_task_count
        ),
        "failed_task_count": (
            result.failed_task_count
        ),
        "error": result.error,
    }

    execution_record = (
        save_execution_record(
            db,
            approval_uid=approval_uid,
            business_uid=business_uid,
            objective=plan.objective,
            execution_result=(
                execution_result
            ),
        )
    )

    execution_result[
        "execution_uid"
    ] = execution_record.execution_uid

    return execution_result

async def execute_action(
    decision_type: str,
    db,
    payload: dict[str, Any],
    approval_uid: str,
    business_uid: str,
) -> dict[str, Any]:
    normalized_type = (
        normalize_name(
            decision_type
        ).replace(
            " ",
            "_",
        )
    )

    if (
        normalized_type
        == "executive_action"
    ):
        return (
            await execute_executive_action(
                db,
                payload,
                approval_uid,
                business_uid,
            )
        )

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
        approval_uid,
        business_uid,
    )


async def execute_approval(
    approval_uid: str,
    *,
    business_uid: str,
) -> dict[str, Any]:
    db = SessionLocal()

    try:
        approval = (
            db.query(CEOApproval)
            .filter(
                CEOApproval.approval_uid
                == approval_uid,
                CEOApproval.business_uid
                == business_uid,
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

        execution_result = (
            await execute_action(
                approval.decision_type,
                db,
                payload,
                approval.approval_uid,
                business_uid,
            )
        )

        payload[
            "execution_result"
        ] = execution_result

        approval.payload_json = (
            json.dumps(
                payload,
                ensure_ascii=False,
                default=str,
            )
        )

        approval.status = "executed"
        approval.executed_at = (
            utc_now()
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
