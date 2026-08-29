from __future__ import annotations

from collections.abc import Generator

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.models import User
from app.bootstrap.routes import register_routes
from app.business.models import (
    BusinessProfile,
    IndustryType,
)
from app.database.database import Base, get_db
from app.database.models import BusinessMembership
from app.repositories.business_repository import BusinessRepository


def build_app() -> tuple[
    TestClient,
    sessionmaker,
]:
    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    app = FastAPI()
    register_routes(app)

    def override_get_db() -> Generator[
        Session,
        None,
        None,
    ]:
        db = testing_session_local()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = (
        override_get_db
    )

    return (
        TestClient(app),
        testing_session_local,
    )


def create_user(
    session_factory: sessionmaker,
    *,
    user_uid: str,
    email: str,
) -> None:
    with session_factory() as db:
        db.add(
            User(
                user_uid=user_uid,
                email=email,
                password_hash="not-used",
                is_active=True,
            )
        )
        db.commit()


def create_business(
    session_factory: sessionmaker,
    *,
    business_uid: str,
    name: str,
) -> None:
    with session_factory() as db:
        BusinessRepository(db).create(
            BusinessProfile(
                id=business_uid,
                name=name,
                industry=IndustryType.OTHER,
                country="Australia",
            )
        )


def create_membership(
    session_factory: sessionmaker,
    *,
    membership_uid: str,
    user_uid: str,
    business_uid: str,
    role: str = "member",
    is_active: bool = True,
) -> None:
    with session_factory() as db:
        db.add(
            BusinessMembership(
                membership_uid=membership_uid,
                user_uid=user_uid,
                business_uid=business_uid,
                role=role,
                is_active=is_active,
            )
        )
        db.commit()


def auth_headers(
    client: TestClient,
    *,
    email: str,
    password: str,
) -> dict[str, str]:
    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "full_name": "Workspace User",
            "password": password,
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


def test_business_list_returns_only_membership_businesses() -> None:
    client, session_factory = build_app()

    headers = auth_headers(
        client,
        email="owner@example.com",
        password="StrongPassword123!",
    )

    with session_factory() as db:
        user = (
            db.query(User)
            .filter(
                User.email == "owner@example.com"
            )
            .one()
        )

        user_uid = user.user_uid

    create_business(
        session_factory,
        business_uid="biz_owned",
        name="Owned Business",
    )
    create_business(
        session_factory,
        business_uid="biz_other",
        name="Other Business",
    )

    create_membership(
        session_factory,
        membership_uid="mem_owned",
        user_uid=user_uid,
        business_uid="biz_owned",
        role="owner",
    )

    response = client.get(
        "/businesses",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["count"] == 1
    assert len(body["businesses"]) == 1
    assert (
        body["businesses"][0]["business_uid"]
        == "biz_owned"
    )


def test_business_list_ignores_inactive_memberships() -> None:
    client, session_factory = build_app()

    headers = auth_headers(
        client,
        email="member@example.com",
        password="StrongPassword123!",
    )

    with session_factory() as db:
        user = (
            db.query(User)
            .filter(
                User.email == "member@example.com"
            )
            .one()
        )

        user_uid = user.user_uid

    create_business(
        session_factory,
        business_uid="biz_active",
        name="Active Business",
    )
    create_business(
        session_factory,
        business_uid="biz_inactive",
        name="Inactive Business",
    )

    create_membership(
        session_factory,
        membership_uid="mem_active",
        user_uid=user_uid,
        business_uid="biz_active",
    )
    create_membership(
        session_factory,
        membership_uid="mem_inactive",
        user_uid=user_uid,
        business_uid="biz_inactive",
        is_active=False,
    )

    response = client.get(
        "/businesses",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["count"] == 1
    assert (
        body["businesses"][0]["business_uid"]
        == "biz_active"
    )


def test_business_list_returns_empty_for_user_without_memberships() -> None:
    client, _session_factory = build_app()

    headers = auth_headers(
        client,
        email="new@example.com",
        password="StrongPassword123!",
    )

    response = client.get(
        "/businesses",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["businesses"] == []
    assert response.json()["count"] == 0


def test_business_list_paginates_only_accessible_businesses() -> None:
    client, session_factory = build_app()

    headers = auth_headers(
        client,
        email="pagination@example.com",
        password="StrongPassword123!",
    )

    with session_factory() as db:
        user = (
            db.query(User)
            .filter(
                User.email == "pagination@example.com"
            )
            .one()
        )
        user_uid = user.user_uid

    create_business(
        session_factory,
        business_uid="biz_accessible_1",
        name="First Accessible Business",
    )
    create_membership(
        session_factory,
        membership_uid="mem_accessible_1",
        user_uid=user_uid,
        business_uid="biz_accessible_1",
        role="owner",
    )

    create_business(
        session_factory,
        business_uid="biz_accessible_2",
        name="Second Accessible Business",
    )
    create_membership(
        session_factory,
        membership_uid="mem_accessible_2",
        user_uid=user_uid,
        business_uid="biz_accessible_2",
        role="member",
    )

    # This business is created last, so it is newest globally.
    # It has no membership for the authenticated user.
    create_business(
        session_factory,
        business_uid="biz_inaccessible",
        name="Newest Inaccessible Business",
    )

    first_response = client.get(
        "/businesses",
        headers=headers,
        params={
            "offset": 0,
            "limit": 1,
        },
    )

    second_response = client.get(
        "/businesses",
        headers=headers,
        params={
            "offset": 1,
            "limit": 1,
        },
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_body = first_response.json()
    second_body = second_response.json()

    assert first_body["offset"] == 0
    assert first_body["limit"] == 1
    assert first_body["count"] == 1

    assert second_body["offset"] == 1
    assert second_body["limit"] == 1
    assert second_body["count"] == 1

    first_uid = (
        first_body["businesses"][0]["business_uid"]
    )
    second_uid = (
        second_body["businesses"][0]["business_uid"]
    )

    accessible_uids = {
        "biz_accessible_1",
        "biz_accessible_2",
    }

    assert first_uid in accessible_uids
    assert second_uid in accessible_uids
    assert first_uid != second_uid

    assert "biz_inaccessible" not in {
        first_uid,
        second_uid,
    }


def test_business_read_allows_active_member() -> None:
    client, session_factory = build_app()

    headers = auth_headers(
        client,
        email="reader@example.com",
        password="StrongPassword123!",
    )

    with session_factory() as db:
        user = (
            db.query(User)
            .filter(
                User.email == "reader@example.com"
            )
            .one()
        )

        user_uid = user.user_uid

    create_business(
        session_factory,
        business_uid="biz_readable",
        name="Readable Business",
    )

    create_membership(
        session_factory,
        membership_uid="mem_readable",
        user_uid=user_uid,
        business_uid="biz_readable",
        role="member",
    )

    response = client.get(
        "/businesses/biz_readable",
        headers=headers,
    )

    assert response.status_code == 200
    assert (
        response.json()["business_uid"]
        == "biz_readable"
    )


def test_business_read_rejects_non_member() -> None:
    client, session_factory = build_app()

    headers = auth_headers(
        client,
        email="outsider@example.com",
        password="StrongPassword123!",
    )

    create_business(
        session_factory,
        business_uid="biz_private",
        name="Private Business",
    )

    response = client.get(
        "/businesses/biz_private",
        headers=headers,
    )

    assert response.status_code == 403


def test_business_read_rejects_inactive_member() -> None:
    client, session_factory = build_app()

    headers = auth_headers(
        client,
        email="inactive-reader@example.com",
        password="StrongPassword123!",
    )

    with session_factory() as db:
        user = (
            db.query(User)
            .filter(
                User.email
                == "inactive-reader@example.com"
            )
            .one()
        )

        user_uid = user.user_uid

    create_business(
        session_factory,
        business_uid="biz_inactive_read",
        name="Inactive Read Business",
    )

    create_membership(
        session_factory,
        membership_uid="mem_inactive_read",
        user_uid=user_uid,
        business_uid="biz_inactive_read",
        role="member",
        is_active=False,
    )

    response = client.get(
        "/businesses/biz_inactive_read",
        headers=headers,
    )

    assert response.status_code == 403


def test_business_update_allows_owner() -> None:
    client, session_factory = build_app()

    headers = auth_headers(
        client,
        email="update-owner@example.com",
        password="StrongPassword123!",
    )

    with session_factory() as db:
        user = (
            db.query(User)
            .filter(
                User.email
                == "update-owner@example.com"
            )
            .one()
        )
        user_uid = user.user_uid

    create_business(
        session_factory,
        business_uid="biz_update_owner",
        name="Owner Update Business",
    )

    create_membership(
        session_factory,
        membership_uid="mem_update_owner",
        user_uid=user_uid,
        business_uid="biz_update_owner",
        role="owner",
    )

    payload = {
        "name": "Owner Updated Business",
        "industry": "other",
        "country": "Australia",
    }

    response = client.put(
        "/businesses/biz_update_owner",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 200


def test_business_update_allows_admin() -> None:
    client, session_factory = build_app()

    headers = auth_headers(
        client,
        email="update-admin@example.com",
        password="StrongPassword123!",
    )

    with session_factory() as db:
        user = (
            db.query(User)
            .filter(
                User.email
                == "update-admin@example.com"
            )
            .one()
        )
        user_uid = user.user_uid

    create_business(
        session_factory,
        business_uid="biz_update_admin",
        name="Admin Update Business",
    )

    create_membership(
        session_factory,
        membership_uid="mem_update_admin",
        user_uid=user_uid,
        business_uid="biz_update_admin",
        role="admin",
    )

    payload = {
        "name": "Admin Updated Business",
        "industry": "other",
        "country": "Australia",
    }

    response = client.put(
        "/businesses/biz_update_admin",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 200


def test_business_update_rejects_member() -> None:
    client, session_factory = build_app()

    headers = auth_headers(
        client,
        email="update-member@example.com",
        password="StrongPassword123!",
    )

    with session_factory() as db:
        user = (
            db.query(User)
            .filter(
                User.email
                == "update-member@example.com"
            )
            .one()
        )
        user_uid = user.user_uid

    create_business(
        session_factory,
        business_uid="biz_update_member",
        name="Member Update Business",
    )

    create_membership(
        session_factory,
        membership_uid="mem_update_member",
        user_uid=user_uid,
        business_uid="biz_update_member",
        role="member",
    )

    payload = {
        "name": "Member Must Not Update",
        "industry": "other",
        "country": "Australia",
    }

    response = client.put(
        "/businesses/biz_update_member",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 403


def test_business_update_rejects_non_member() -> None:
    client, session_factory = build_app()

    headers = auth_headers(
        client,
        email="update-outsider@example.com",
        password="StrongPassword123!",
    )

    create_business(
        session_factory,
        business_uid="biz_update_private",
        name="Private Update Business",
    )

    payload = {
        "name": "Outsider Must Not Update",
        "industry": "other",
        "country": "Australia",
    }

    response = client.put(
        "/businesses/biz_update_private",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 403


def test_business_delete_allows_owner() -> None:
    client, session_factory = build_app()

    headers = auth_headers(
        client,
        email="delete-owner@example.com",
        password="StrongPassword123!",
    )

    with session_factory() as db:
        user = (
            db.query(User)
            .filter(
                User.email
                == "delete-owner@example.com"
            )
            .one()
        )
        user_uid = user.user_uid

    create_business(
        session_factory,
        business_uid="biz_delete_owner",
        name="Owner Delete Business",
    )

    create_membership(
        session_factory,
        membership_uid="mem_delete_owner",
        user_uid=user_uid,
        business_uid="biz_delete_owner",
        role="owner",
    )

    response = client.delete(
        "/businesses/biz_delete_owner",
        headers=headers,
    )

    assert response.status_code == 200


def test_business_delete_rejects_admin() -> None:
    client, session_factory = build_app()

    headers = auth_headers(
        client,
        email="delete-admin@example.com",
        password="StrongPassword123!",
    )

    with session_factory() as db:
        user = (
            db.query(User)
            .filter(
                User.email
                == "delete-admin@example.com"
            )
            .one()
        )
        user_uid = user.user_uid

    create_business(
        session_factory,
        business_uid="biz_delete_admin",
        name="Admin Delete Business",
    )

    create_membership(
        session_factory,
        membership_uid="mem_delete_admin",
        user_uid=user_uid,
        business_uid="biz_delete_admin",
        role="admin",
    )

    response = client.delete(
        "/businesses/biz_delete_admin",
        headers=headers,
    )

    assert response.status_code == 403


def test_business_delete_rejects_member() -> None:
    client, session_factory = build_app()

    headers = auth_headers(
        client,
        email="delete-member@example.com",
        password="StrongPassword123!",
    )

    with session_factory() as db:
        user = (
            db.query(User)
            .filter(
                User.email
                == "delete-member@example.com"
            )
            .one()
        )
        user_uid = user.user_uid

    create_business(
        session_factory,
        business_uid="biz_delete_member",
        name="Member Delete Business",
    )

    create_membership(
        session_factory,
        membership_uid="mem_delete_member",
        user_uid=user_uid,
        business_uid="biz_delete_member",
        role="member",
    )

    response = client.delete(
        "/businesses/biz_delete_member",
        headers=headers,
    )

    assert response.status_code == 403


def test_business_delete_rejects_non_member() -> None:
    client, session_factory = build_app()

    headers = auth_headers(
        client,
        email="delete-outsider@example.com",
        password="StrongPassword123!",
    )

    create_business(
        session_factory,
        business_uid="biz_delete_private",
        name="Private Delete Business",
    )

    response = client.delete(
        "/businesses/biz_delete_private",
        headers=headers,
    )

    assert response.status_code == 403



def test_business_role_helper_allows_consultant_read_role() -> None:
    from app.services.business_membership_service import (
        user_has_business_role,
    )

    client, session_factory = build_app()

    auth_headers(
        client,
        email="role-helper@example.com",
        password="StrongPassword123!",
    )

    with session_factory() as db:
        user = (
            db.query(User)
            .filter(
                User.email == "role-helper@example.com"
            )
            .one()
        )
        user_uid = user.user_uid

    create_business(
        session_factory,
        business_uid="biz_role_helper",
        name="Role Helper Business",
    )

    create_membership(
        session_factory,
        membership_uid="mem_role_helper",
        user_uid=user_uid,
        business_uid="biz_role_helper",
        role="consultant",
    )

    with session_factory() as db:
        assert user_has_business_role(
            db,
            user_uid=user_uid,
            business_uid="biz_role_helper",
            allowed_roles={"member", "consultant"},
        )

        assert not user_has_business_role(
            db,
            user_uid=user_uid,
            business_uid="biz_role_helper",
            allowed_roles={"owner", "admin"},
        )


def test_business_role_helper_rejects_inactive_owner() -> None:
    from app.services.business_membership_service import (
        user_has_business_role,
    )

    client, session_factory = build_app()

    auth_headers(
        client,
        email="inactive-role@example.com",
        password="StrongPassword123!",
    )

    with session_factory() as db:
        user = (
            db.query(User)
            .filter(
                User.email == "inactive-role@example.com"
            )
            .one()
        )
        user_uid = user.user_uid

    create_business(
        session_factory,
        business_uid="biz_inactive_role",
        name="Inactive Role Business",
    )

    create_membership(
        session_factory,
        membership_uid="mem_inactive_role",
        user_uid=user_uid,
        business_uid="biz_inactive_role",
        role="owner",
        is_active=False,
    )

    with session_factory() as db:
        assert not user_has_business_role(
            db,
            user_uid=user_uid,
            business_uid="biz_inactive_role",
            allowed_roles={"owner"},
        )



def test_business_delete_removes_all_business_memberships() -> None:
    client, session_factory = build_app()

    owner_headers = auth_headers(
        client,
        email="delete-owner@example.com",
        password="StrongPassword123!",
    )

    auth_headers(
        client,
        email="delete-member@example.com",
        password="StrongPassword123!",
    )

    with session_factory() as db:
        owner = (
            db.query(User)
            .filter(
                User.email == "delete-owner@example.com"
            )
            .one()
        )
        member = (
            db.query(User)
            .filter(
                User.email == "delete-member@example.com"
            )
            .one()
        )

        owner_uid = owner.user_uid
        member_uid = member.user_uid

    create_business(
        session_factory,
        business_uid="biz_delete_cleanup",
        name="Delete Cleanup Business",
    )

    create_membership(
        session_factory,
        membership_uid="mem_delete_cleanup_owner",
        user_uid=owner_uid,
        business_uid="biz_delete_cleanup",
        role="owner",
    )

    create_membership(
        session_factory,
        membership_uid="mem_delete_cleanup_member",
        user_uid=member_uid,
        business_uid="biz_delete_cleanup",
        role="member",
    )

    response = client.delete(
        "/businesses/biz_delete_cleanup",
        headers=owner_headers,
    )

    assert response.status_code == 200

    with session_factory() as db:
        remaining_memberships = (
            db.query(BusinessMembership)
            .filter(
                BusinessMembership.business_uid
                == "biz_delete_cleanup"
            )
            .all()
        )

        assert remaining_memberships == []
