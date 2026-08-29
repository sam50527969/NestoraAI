from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.models import User
from app.auth.security import hash_password
from app.database.models import (
    Base,
    Business,
    BusinessMembership,
)
from app.services.business_membership_service import (
    create_membership,
    get_membership,
    list_user_memberships,
    user_can_access_business,
)


def build_db():
    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    return engine, Session()


def seed_identity(db):
    user = User(
        user_uid="usr-membership-test",
        email="membership@example.com",
        full_name="Membership Test",
        password_hash=hash_password(
            "TestingPassword123!"
        ),
        role="user",
        is_active=True,
    )

    business_a = Business(
        business_uid="biz-membership-a",
        name="Business A",
        industry="OTHER",
        country="Australia",
        currency="AUD",
    )

    business_b = Business(
        business_uid="biz-membership-b",
        name="Business B",
        industry="OTHER",
        country="Canada",
        currency="CAD",
    )

    db.add_all(
        [
            user,
            business_a,
            business_b,
        ]
    )

    db.commit()

    return user, business_a, business_b


def test_user_can_have_multiple_business_memberships():
    engine, db = build_db()

    try:
        user, business_a, business_b = (
            seed_identity(db)
        )

        owner = create_membership(
            db,
            user_uid=user.user_uid,
            business_uid=(
                business_a.business_uid
            ),
            role="owner",
        )

        consultant = create_membership(
            db,
            user_uid=user.user_uid,
            business_uid=(
                business_b.business_uid
            ),
            role="consultant",
        )

        assert owner.role == "owner"
        assert consultant.role == "consultant"

        memberships = list_user_memberships(
            db,
            user.user_uid,
        )

        assert len(memberships) == 2

        assert user_can_access_business(
            db,
            user_uid=user.user_uid,
            business_uid=(
                business_a.business_uid
            ),
        )

        assert user_can_access_business(
            db,
            user_uid=user.user_uid,
            business_uid=(
                business_b.business_uid
            ),
        )

    finally:
        db.close()
        engine.dispose()


def test_duplicate_membership_is_rejected():
    engine, db = build_db()

    try:
        user, business_a, _ = seed_identity(
            db
        )

        create_membership(
            db,
            user_uid=user.user_uid,
            business_uid=(
                business_a.business_uid
            ),
            role="owner",
        )

        try:
            create_membership(
                db,
                user_uid=user.user_uid,
                business_uid=(
                    business_a.business_uid
                ),
                role="admin",
            )
        except ValueError as exc:
            assert (
                "already has a membership"
                in str(exc)
            )
        else:
            raise AssertionError(
                "Duplicate membership "
                "was accepted."
            )

    finally:
        db.close()
        engine.dispose()


def test_inactive_membership_denies_access():
    engine, db = build_db()

    try:
        user, business_a, _ = seed_identity(
            db
        )

        membership = create_membership(
            db,
            user_uid=user.user_uid,
            business_uid=(
                business_a.business_uid
            ),
            role="member",
        )

        membership.is_active = False
        db.commit()

        assert not user_can_access_business(
            db,
            user_uid=user.user_uid,
            business_uid=(
                business_a.business_uid
            ),
        )

        assert (
            list_user_memberships(
                db,
                user.user_uid,
            )
            == []
        )

        all_memberships = (
            list_user_memberships(
                db,
                user.user_uid,
                active_only=False,
            )
        )

        assert len(all_memberships) == 1

    finally:
        db.close()
        engine.dispose()


def test_membership_requires_valid_identity():
    engine, db = build_db()

    try:
        _, business_a, _ = seed_identity(
            db
        )

        try:
            create_membership(
                db,
                user_uid="usr-missing",
                business_uid=(
                    business_a.business_uid
                ),
                role="owner",
            )
        except ValueError as exc:
            assert "does not exist" in str(exc)
        else:
            raise AssertionError(
                "Missing user was accepted."
            )

    finally:
        db.close()
        engine.dispose()


def test_membership_orm_matches_migration():
    columns = {
        column.name
        for column
        in BusinessMembership.__table__.columns
    }

    assert columns == {
        "id",
        "membership_uid",
        "user_uid",
        "business_uid",
        "role",
        "is_active",
        "created_at",
        "updated_at",
    }
