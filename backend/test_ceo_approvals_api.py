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

from app.business.access import (
    get_current_business_uid,
)
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

    app.dependency_overrides[
        get_current_business_uid
    ] = lambda: "biz_atlas"

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
            business_uid="biz_atlas",
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

def test_approval_isolated_by_workspace(
    approval_api,
):
    client, session_factory = approval_api

    db = session_factory()

    try:
        dental = CEOApproval(
            approval_uid="apr_dental_private",
            business_uid="biz_dental",
            decision_type="crm_outreach",
            title="Dental private approval",
            description=(
                "Must never be visible to Atlas."
            ),
            source_type="executive_report",
            source_uid="dental_report_private",
            status="pending",
            requested_by="CEO Agent",
            payload_json="{}",
        )

        legacy = CEOApproval(
            approval_uid="apr_legacy_null",
            business_uid=None,
            decision_type="crm_outreach",
            title="Legacy unowned approval",
            description=(
                "Legacy rows must not leak."
            ),
            source_type="executive_report",
            source_uid="legacy_report",
            status="pending",
            requested_by="CEO Agent",
            payload_json="{}",
        )

        db.add_all([
            dental,
            legacy,
        ])
        db.commit()

    finally:
        db.close()

    atlas = create_approval(
        client,
        title="Atlas visible approval",
        source_uid="atlas_report_visible",
    )

    assert atlas["business_uid"] == "biz_atlas"

    response = client.get(
        "/ceo-approvals"
    )
    assert response.status_code == 200

    approvals = response.json()

    approval_uids = {
        item["approval_uid"]
        for item in approvals
    }

    assert atlas["approval_uid"] in approval_uids
    assert (
        "apr_dental_private"
        not in approval_uids
    )
    assert (
        "apr_legacy_null"
        not in approval_uids
    )

    protected_urls = [
        (
            "get",
            "/ceo-approvals/"
            "apr_dental_private",
            None,
        ),
        (
            "post",
            "/ceo-approvals/"
            "apr_dental_private/approve",
            {
                "reviewed_by": "Atlas CEO",
            },
        ),
        (
            "post",
            "/ceo-approvals/"
            "apr_dental_private/reject",
            {
                "reviewed_by": "Atlas CEO",
            },
        ),
        (
            "post",
            "/ceo-approvals/"
            "apr_dental_private/execute",
            None,
        ),
        (
            "get",
            "/ceo-approvals/"
            "apr_legacy_null",
            None,
        ),
    ]

    for method, url, payload in protected_urls:
        if method == "get":
            response = client.get(url)
        else:
            response = client.post(
                url,
                json=payload,
            )

        assert response.status_code == 404

    db = session_factory()

    try:
        dental = (
            db.query(CEOApproval)
            .filter(
                CEOApproval.approval_uid
                == "apr_dental_private"
            )
            .one()
        )

        legacy = (
            db.query(CEOApproval)
            .filter(
                CEOApproval.approval_uid
                == "apr_legacy_null"
            )
            .one()
        )

        assert dental.status == "pending"
        assert dental.reviewed_by is None
        assert dental.executed_at is None

        assert legacy.status == "pending"
        assert legacy.reviewed_by is None
        assert legacy.executed_at is None

    finally:
        db.close()


def test_duplicate_approval_is_workspace_scoped(
    approval_api,
):
    client, session_factory = approval_api

    db = session_factory()

    try:
        dental = CEOApproval(
            approval_uid="apr_dental_duplicate",
            business_uid="biz_dental",
            decision_type="crm_outreach",
            title="Shared duplicate title",
            description=(
                "Same duplicate description."
            ),
            source_type="executive_report",
            source_uid="shared_duplicate_source",
            status="pending",
            requested_by="CEO Agent",
            payload_json="{}",
        )

        db.add(dental)
        db.commit()

    finally:
        db.close()

    atlas = create_approval(
        client,
        title="Shared duplicate title",
        description=(
            "Same duplicate description."
        ),
        source_uid="shared_duplicate_source",
    )

    assert (
        atlas["approval_uid"]
        != "apr_dental_duplicate"
    )
    assert atlas["business_uid"] == "biz_atlas"

    second_atlas = create_approval(
        client,
        title="Shared duplicate title",
        description=(
            "Same duplicate description."
        ),
        source_uid="shared_duplicate_source",
    )

    assert (
        second_atlas["approval_uid"]
        == atlas["approval_uid"]
    )

    db = session_factory()

    try:
        matching = (
            db.query(CEOApproval)
            .filter(
                CEOApproval.title
                == "Shared duplicate title"
            )
            .all()
        )

        assert len(matching) == 2

        owners = {
            item.business_uid
            for item in matching
        }

        assert owners == {
            "biz_atlas",
            "biz_dental",
        }

    finally:
        db.close()

def test_crm_execution_cannot_use_foreign_workspace_lead(
    approval_api,
):
    client, session_factory = approval_api

    db = session_factory()

    try:
        atlas = Lead(
            business_uid="biz_atlas",
            name="Atlas Local Prospect",
            category="Fleet Services",
            phone="+971500000001",
            website="https://atlas-prospect.example",
            priority="high",
            ai_score=80,
            estimated_value=5000,
        )

        dental = Lead(
            business_uid="biz_dental",
            name="Dental Foreign Prospect",
            category="Dental",
            phone="+974500000002",
            website="https://dental-prospect.example",
            priority="high",
            ai_score=100,
            estimated_value=50000,
        )

        db.add_all([
            atlas,
            dental,
        ])
        db.commit()

        db.refresh(atlas)
        db.refresh(dental)

        atlas_lead_id = atlas.id
        dental_lead_id = dental.id

    finally:
        db.close()

    created = create_approval(
        client,
        title=(
            "Atlas workspace outreach "
            "isolation"
        ),
        source_uid=(
            "atlas_workspace_outreach_test"
        ),
        payload={
            "high_priority_count": 1,
            "offer": "Atlas service package",
        },
    )

    approval_uid = created["approval_uid"]

    approve_response = client.post(
        (
            f"/ceo-approvals/"
            f"{approval_uid}/approve"
        ),
        json={
            "reviewed_by": "Atlas CEO",
            "decision_note": (
                "Approved for Atlas only."
            ),
        },
    )

    assert approve_response.status_code == 200

    execute_response = client.post(
        (
            f"/ceo-approvals/"
            f"{approval_uid}/execute"
        )
    )

    assert execute_response.status_code == 200

    executed = execute_response.json()

    result = executed["payload"][
        "execution_result"
    ]

    assert result["prepared_count"] == 1

    packages = result["outreach_packages"]

    assert len(packages) == 1

    assert (
        packages[0]["lead_id"]
        == atlas_lead_id
    )

    assert (
        packages[0]["lead_name"]
        == "Atlas Local Prospect"
    )

    assert (
        packages[0]["lead_id"]
        != dental_lead_id
    )

    db = session_factory()

    try:
        activities = (
            db.query(OutreachActivity)
            .filter(
                OutreachActivity.approval_uid
                == approval_uid
            )
            .all()
        )

        assert len(activities) == 1

        assert (
            activities[0].lead_id
            == atlas_lead_id
        )

        assert (
            activities[0].lead_id
            != dental_lead_id
        )

        foreign_activity_count = (
            db.query(OutreachActivity)
            .filter(
                OutreachActivity.lead_id
                == dental_lead_id
            )
            .count()
        )

        assert foreign_activity_count == 0

    finally:
        db.close()
