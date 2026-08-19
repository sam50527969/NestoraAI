from datetime import (
    UTC,
    datetime,
    timedelta,
)
import uuid

import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash

from app.config import (
    AUTH_ACCESS_TOKEN_MINUTES,
    AUTH_ALGORITHM,
    AUTH_SECRET_KEY,
)


TOKEN_ISSUER = "nestora-api"
TOKEN_TYPE = "access"

password_hasher = (
    PasswordHash.recommended()
)

DUMMY_PASSWORD_HASH = (
    password_hasher.hash(
        "nestora-dummy-password"
    )
)


def hash_password(
    password: str,
) -> str:
    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    return password_hasher.verify(
        plain_password,
        password_hash,
    )


def create_access_token(
    user_uid: str,
) -> tuple[str, int]:
    expires_in = (
        AUTH_ACCESS_TOKEN_MINUTES
        * 60
    )

    issued_at = datetime.now(UTC)

    expires_at = (
        issued_at
        + timedelta(
            seconds=expires_in,
        )
    )

    payload = {
        "sub": user_uid,
        "type": TOKEN_TYPE,
        "iss": TOKEN_ISSUER,
        "iat": issued_at,
        "exp": expires_at,
        "jti": uuid.uuid4().hex,
    }

    token = jwt.encode(
        payload,
        AUTH_SECRET_KEY,
        algorithm=AUTH_ALGORITHM,
    )

    return token, expires_in


def decode_access_token(
    token: str,
) -> str | None:
    try:
        payload = jwt.decode(
            token,
            AUTH_SECRET_KEY,
            algorithms=[
                AUTH_ALGORITHM,
            ],
            issuer=TOKEN_ISSUER,
            options={
                "require": [
                    "sub",
                    "type",
                    "iss",
                    "iat",
                    "exp",
                ],
            },
        )
    except InvalidTokenError:
        return None

    if payload.get("type") != TOKEN_TYPE:
        return None

    user_uid = payload.get("sub")

    if not isinstance(user_uid, str):
        return None

    cleaned_uid = user_uid.strip()

    return cleaned_uid or None