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
from app.auth.models import User
from app.auth.schemas import (
    LoginRequest,
    TokenResponse,
    UserRegister,
    UserResponse,
)
from app.auth.security import (
    create_access_token,
)
from app.auth.service import (
    authenticate_user,
    create_user,
)
from app.database.database import get_db


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
    user = authenticate_user(
        db,
        data.email,
        data.password,
    )

    if user is None:
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