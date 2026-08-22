from types import SimpleNamespace
import warnings

import pytest
from fastapi import FastAPI

with warnings.catch_warnings():
    warnings.simplefilter("ignore")

    from fastapi.testclient import (
        TestClient,
    )

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.approvals import (
    executor as approval_executor,
)
from app.approvals import (
    service as approval_service,
)
from app.approvals.models import CEOApproval
from app.approvals.routes import (
    router as approval_router,
)
from app.database.database import Base
from app.database.models import Lead
from app.outreach_activity.models import (
    OutreachActivity,
)


@pytest.fixture()
def approval_api(
    monkeypatch,
):
    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(
        bind=engine,
        tables=[
            Lead.__table__,
            CEOApproval.__table__,
            OutreachActivity.__table__,
        ],
    )

    monkeypatch.setattr(
        approval_service,
        "SessionLocal",
        session_factory,
    )

    monkeypatch.setattr(
        approval_executor,
        "SessionLocal",
        session_factory,
    )

    def fake_generate_outreach(
        request,
    ):
        lead_name = request.lead.name

        return SimpleNamespace(
            email_subject=(
                f"Business opportunity for "
                f"{lead_name}"
            ),
            email_body=(
                f"Prepared email for "
                f"{lead_name}."
            ),
            whatsapp_message=(
                f"Prepared WhatsApp message "
                f"for {lead_name}."
            ),
            cold_call_script=(
                f"Prepared call script for "
                f"{lead_name}."
            ),
            proposal_summary=(
                f"Prepared proposal for "
                f"{lead_name}."
            ),
        )

    monkeypatch.setattr(
        approval_executor,
        "generate_outreach",
        fake_generate_outreach,
    )

    app = FastAPI()
    app.include_router(
        approval_router
    )

    with TestClient(app) as client:
        yield client, session_factory

    Base.metadata.drop_all(
        bind=engine,
        tables=[
            OutreachActivity.__table__,
            CEOApproval.__table__,
            Lead.__table__,
        ],
    )

    engine.dispose()


def create_approval(
    client: TestClient,
    *,
    title: str = (
        "Prepare priority CRM outreach"
    ),
    description: str = (
        "Prepare outreach for the highest "
        "priority CRM opportunities."
    ),
    decision_type: str = "crm_outreach",
    source_uid: str = "report_test_001",
    payload: dict | None = None,
):
    response = client.post(
        "/ceo-approvals",
        json={
            "title": title,
            "description": description,
            "decision_type": (
                decision_type
            ),
            "source_type": (
                "executive_report"
            ),
            "source_uid": source_uid,
            "requested_by": "CEO Agent",
            "payload": (
                payload
                if payload is not None
                else {
                    "high_priority_count": 1,
                    "offer": (
                        "Nestora growth "
                        "package"
                    ),
                }
            ),
        },
    )

    assert response.status_code == 201

    return response.json()


def approve_request(
    client: TestClient,
    approval_uid: str,
):
    response = client.post(
        (
            f"/ceo-approvals/"
            f"{approval_uid}/approve"
        ),
        json={
            "reviewed_by": "CEO",
            "decision_note": (
                "Approved during API testing."
            ),
        },
    )

    assert response.status_code == 200

    return response.json()


def add_high_priority_lead(
    session_factory,
) -> int:
    db = session_factory()

    try:
        lead = Lead(
            name="Gulf Neon Advertising",
            category="Advertising",
            phone="+97455550000",
            website=(
                "https://gulfneon.example"
            ),
            status="New",
            priority="High",
            notes=(
                "Priority outreach test lead."
            ),
            ai_score=92,
            estimated_value=25000,
        )

        db.add(lead)
        db.commit()
        db.refresh(lead)

        return lead.id

    finally:
        db.close()


def test_create_list_and_get_approval(
    approval_api,
):
    client, _ = approval_api

    created = create_approval(client)

    assert created["status"] == "pending"
    assert (
        created["decision_type"]
        == "crm_outreach"
    )
    assert (
        created["payload"][
            "high_priority_count"
        ]
        == 1
    )

    approval_uid = created[
        "approval_uid"
    ]

    get_response = client.get(
        f"/ceo-approvals/{approval_uid}"
    )

    assert get_response.status_code == 200
    assert (
        get_response.json()[
            "approval_uid"
        ]
        == approval_uid
    )

    list_response = client.get(
        "/ceo-approvals",
        params={
            "status": "pending",
            "limit": 10,
        },
    )

    assert (
        list_response.status_code
        == 200
    )

    approvals = list_response.json()

    assert len(approvals) == 1
    assert (
        approvals[0]["approval_uid"]
        == approval_uid
    )


def test_duplicate_active_approval_is_reused(
    approval_api,
):
    client, session_factory = (
        approval_api
    )

    first = create_approval(client)
    second = create_approval(client)

    assert (
        first["approval_uid"]
        == second["approval_uid"]
    )

    db = session_factory()

    try:
        assert (
            db.query(CEOApproval).count()
            == 1
        )

    finally:
        db.close()


def test_approve_and_prevent_second_decision(
    approval_api,
):
    client, _ = approval_api

    created = create_approval(client)

    approval_uid = created[
        "approval_uid"
    ]

    approved = approve_request(
        client,
        approval_uid,
    )

    assert (
        approved["status"]
        == "approved"
    )
    assert (
        approved["reviewed_by"]
        == "CEO"
    )
    assert (
        approved["reviewed_at"]
        is not None
    )

    repeated_response = client.post(
        (
            f"/ceo-approvals/"
            f"{approval_uid}/reject"
        ),
        json={
            "reviewed_by": "CEO",
            "decision_note": (
                "Attempted second decision."
            ),
        },
    )

    assert (
        repeated_response.status_code
        == 409
    )

    assert repeated_response.json() == {
        "detail": (
            "This approval request has "
            "already been reviewed."
        )
    }


def test_rejected_approval_cannot_execute(
    approval_api,
):
    client, _ = approval_api

    created = create_approval(
        client,
        title="Reject this outreach",
        source_uid="report_test_reject",
    )

    approval_uid = created[
        "approval_uid"
    ]

    reject_response = client.post(
        (
            f"/ceo-approvals/"
            f"{approval_uid}/reject"
        ),
        json={
            "reviewed_by": "CEO",
            "decision_note": (
                "Not aligned with current "
                "priorities."
            ),
        },
    )

    assert (
        reject_response.status_code
        == 200
    )
    assert (
        reject_response.json()["status"]
        == "rejected"
    )

    execute_response = client.post(
        (
            f"/ceo-approvals/"
            f"{approval_uid}/execute"
        )
    )

    assert (
        execute_response.status_code
        == 409
    )

    assert execute_response.json() == {
        "detail": (
            "Only approved requests can "
            "be executed."
        )
    }


def test_execute_approved_crm_outreach(
    approval_api,
):
    client, session_factory = (
        approval_api
    )

    lead_id = add_high_priority_lead(
        session_factory
    )

    created = create_approval(
        client,
        title=(
            "Execute CRM outreach package"
        ),
        source_uid=(
            "report_test_execution"
        ),
    )

    approval_uid = created[
        "approval_uid"
    ]

    approve_request(
        client,
        approval_uid,
    )

    execute_response = client.post(
        (
            f"/ceo-approvals/"
            f"{approval_uid}/execute"
        )
    )

    assert (
        execute_response.status_code
        == 200
    )

    executed = (
        execute_response.json()
    )

    assert (
        executed["status"]
        == "executed"
    )
    assert (
        executed["executed_at"]
        is not None
    )

    execution_result = (
        executed["payload"][
            "execution_result"
        ]
    )

    assert (
        execution_result["action_type"]
        == "crm_outreach"
    )
    assert (
        execution_result["status"]
        == "prepared"
    )
    assert (
        execution_result[
            "requested_count"
        ]
        == 1
    )
    assert (
        execution_result[
            "prepared_count"
        ]
        == 1
    )

    outreach_packages = (
        execution_result[
            "outreach_packages"
        ]
    )

    assert (
        len(outreach_packages)
        == 1
    )
    assert (
        outreach_packages[0][
            "lead_id"
        ]
        == lead_id
    )
    assert (
        outreach_packages[0][
            "lead_name"
        ]
        == "Gulf Neon Advertising"
    )

    db = session_factory()

    try:
        activity = (
            db.query(
                OutreachActivity
            )
            .filter(
                OutreachActivity.approval_uid
                == approval_uid
            )
            .one()
        )

        assert (
            activity.lead_id
            == lead_id
        )
        assert (
            activity.lead_name
            == "Gulf Neon Advertising"
        )
        assert (
            activity.status
            == "prepared"
        )
        assert (
            activity.prepared_by
            == "CEO Agent"
        )

        saved_approval = (
            db.query(CEOApproval)
            .filter(
                CEOApproval.approval_uid
                == approval_uid
            )
            .one()
        )

        assert (
            saved_approval.status
            == "executed"
        )
        assert (
            saved_approval.executed_at
            is not None
        )

    finally:
        db.close()


def test_unsupported_action_cannot_execute(
    approval_api,
):
    client, _ = approval_api

    created = create_approval(
        client,
        title="Unsupported executive action",
        decision_type="unknown_action",
        source_uid=(
            "report_test_unsupported"
        ),
        payload={
            "message": (
                "No executor exists."
            ),
        },
    )

    approval_uid = created[
        "approval_uid"
    ]

    approve_request(
        client,
        approval_uid,
    )

    execute_response = client.post(
        (
            f"/ceo-approvals/"
            f"{approval_uid}/execute"
        )
    )

    assert (
        execute_response.status_code
        == 409
    )

    assert execute_response.json() == {
        "detail": (
            "No approved-action executor "
            "is registered for "
            "'unknown_action'."
        )
    }


def test_missing_approval_returns_404(
    approval_api,
):
    client, _ = approval_api

    missing_uid = "apr_missing"

    responses = [
        client.get(
            (
                f"/ceo-approvals/"
                f"{missing_uid}"
            )
        ),
        client.post(
            (
                f"/ceo-approvals/"
                f"{missing_uid}/approve"
            ),
            json={
                "reviewed_by": "CEO",
            },
        ),
        client.post(
            (
                f"/ceo-approvals/"
                f"{missing_uid}/reject"
            ),
            json={
                "reviewed_by": "CEO",
            },
        ),
        client.post(
            (
                f"/ceo-approvals/"
                f"{missing_uid}/execute"
            )
        ),
    ]

    for response in responses:
        assert (
            response.status_code
            == 404
        )

        assert response.json() == {
            "detail": (
                "Approval request was "
                "not found."
            )
        }