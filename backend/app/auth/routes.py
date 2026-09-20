import logging
import uuid
from urllib.parse import urlencode

import httpx

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_user,
)
from app.auth.login_throttle import (
    LOGIN_FAILURE_WINDOW_SECONDS,
    PASSWORD_RESET_REQUEST_WINDOW_SECONDS,
    login_failure_throttle,
    password_reset_throttle,
)
from app.auth.models import User
from app.auth.schemas import (
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    PasswordResetResponse,
    TokenResponse,
    UserRegister,
    UserResponse,
)
from app.auth.security import (
    create_access_token,
    create_password_reset_token,
)
from app.auth.service import (
    authenticate_user,
    create_user,
    get_user_by_email,
    reset_user_password,
)
from app.config import (
    PASSWORD_RESET_FRONTEND_URL,
)
from app.database.database import get_db
from app.outreach_activity.email_delivery import (
    email_provider,
)


logger = logging.getLogger(
    __name__
)

PASSWORD_RESET_REQUEST_MESSAGE = (
    "If an account exists for that email, "
    "a password reset link has been sent."
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=(
        status.HTTP_201_CREATED
    ),
)
def register_user(
    data: UserRegister,
    db: Session = Depends(get_db),
):
    try:
        return create_user(
            db,
            data,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=str(error),
        ) from error


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_user(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    if login_failure_throttle.is_blocked(
        data.email
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_429_TOO_MANY_REQUESTS
            ),
            detail=(
                "Too many failed login attempts. "
                "Please try again later."
            ),
            headers={
                "Retry-After": str(
                    int(
                        LOGIN_FAILURE_WINDOW_SECONDS
                    )
                ),
            },
        )

    user = authenticate_user(
        db,
        data.email,
        data.password,
    )

    if user is None:
        login_failure_throttle.record_failure(
            data.email
        )

        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Email or password is "
                "incorrect."
            ),
            headers={
                "WWW-Authenticate":
                    "Bearer",
            },
        )

    login_failure_throttle.reset(
        data.email
    )

    access_token, expires_in = (
        create_access_token(
            user.user_uid
        )
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        user=user,
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def read_current_user(
    current_user: User = Depends(
        get_current_user
    ),
):
    return current_user



@router.post(
    "/password-reset/request",
    response_model=PasswordResetResponse,
)
def request_password_reset(
    data: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    if password_reset_throttle.is_blocked(
        data.email
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_429_TOO_MANY_REQUESTS
            ),
            detail=(
                "Too many password reset "
                "requests. Please try again later."
            ),
            headers={
                "Retry-After": str(
                    int(
                        PASSWORD_RESET_REQUEST_WINDOW_SECONDS
                    )
                ),
            },
        )

    password_reset_throttle.record_failure(
        data.email
    )

    user = get_user_by_email(
        db,
        data.email,
    )

    if (
        user is not None
        and user.is_active
    ):
        token, expires_in = (
            create_password_reset_token(
                user.user_uid,
                user.password_hash,
            )
        )

        separator = (
            "&"
            if "?"
            in PASSWORD_RESET_FRONTEND_URL
            else "?"
        )

        reset_url = (
            f"{PASSWORD_RESET_FRONTEND_URL}"
            f"{separator}"
            f"{urlencode({
                'reset_token': token
            })}"
        )

        body = (
            "A password reset was requested "
            "for your Nestora account.\n\n"
            f"Reset your password here:\n"
            f"{reset_url}\n\n"
            "This link expires in "
            f"{expires_in // 60} minutes.\n\n"
            "If you did not request this, "
            "you can ignore this email."
        )

        try:
            email_provider.send_email(
                recipient=user.email,
                subject=(
                    "Reset your Nestora password"
                ),
                body=body,
                idempotency_key=(
                    "password-reset/"
                    f"{user.user_uid}/"
                    f"{uuid.uuid4().hex}"
                ),
            )

        except (
            RuntimeError,
            ValueError,
            httpx.HTTPError,
        ):
            logger.error(
                "Password reset email "
                "delivery failed for "
                "user_uid=%s",
                user.user_uid,
            )

    return PasswordResetResponse(
        message=(
            PASSWORD_RESET_REQUEST_MESSAGE
        )
    )


@router.post(
    "/password-reset/confirm",
    response_model=PasswordResetResponse,
)
def confirm_password_reset(
    data: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    user = reset_user_password(
        db,
        token=data.token,
        new_password=data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=(
                "Password reset link is "
                "invalid or expired."
            ),
        )

    login_failure_throttle.reset(
        user.email
    )

    return PasswordResetResponse(
        message=(
            "Password has been reset "
            "successfully."
        )
    )
