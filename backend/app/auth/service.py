from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.schemas import (
    UserRegister,
    normalize_email,
)
from app.auth.security import (
    DUMMY_PASSWORD_HASH,
    hash_password,
    verify_password,
)


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    normalized_email = (
        normalize_email(email)
    )

    return (
        db.query(User)
        .filter(
            User.email
            == normalized_email
        )
        .first()
    )


def get_user_by_uid(
    db: Session,
    user_uid: str,
) -> User | None:
    return (
        db.query(User)
        .filter(
            User.user_uid
            == user_uid.strip()
        )
        .first()
    )


def create_user(
    db: Session,
    data: UserRegister,
) -> User:
    if get_user_by_email(
        db,
        data.email,
    ):
        raise ValueError(
            "An account with this email "
            "already exists."
        )

    user = User(
        email=data.email,
        full_name=data.full_name,
        password_hash=hash_password(
            data.password
        ),
        role="user",
        is_active=True,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:
    user = get_user_by_email(
        db,
        email,
    )

    if user is None:
        verify_password(
            password,
            DUMMY_PASSWORD_HASH,
        )

        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    if not user.is_active:
        return None

    return user