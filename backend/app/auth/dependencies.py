from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.security import (
    decode_access_token,
)
from app.auth.service import (
    get_user_by_uid,
)
from app.database.database import get_db


bearer_scheme = HTTPBearer(
    auto_error=False,
)


def authentication_error() -> HTTPException:
    return HTTPException(
        status_code=(
            status.HTTP_401_UNAUTHORIZED
        ),
        detail=(
            "Authentication credentials "
            "are invalid or expired."
        ),
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )


def get_current_user(
    credentials: (
        HTTPAuthorizationCredentials
        | None
    ) = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise authentication_error()

    user_uid = decode_access_token(
        credentials.credentials
    )

    if user_uid is None:
        raise authentication_error()

    user = get_user_by_uid(
        db,
        user_uid,
    )

    if (
        user is None
        or not user.is_active
    ):
        raise authentication_error()

    return user