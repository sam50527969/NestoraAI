from datetime import (
    UTC,
    datetime,
    timedelta,
)
import hashlib
import hmac
import uuid

import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash

from app.config import (
    AUTH_ACCESS_TOKEN_MINUTES,
    AUTH_ALGORITHM,
    AUTH_SECRET_KEY,
    PASSWORD_RESET_TOKEN_MINUTES,
)


TOKEN_ISSUER = "nestora-api"
TOKEN_TYPE = "access"
PASSWORD_RESET_TOKEN_TYPE = (
    "password_reset"
)

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


def _password_hash_fingerprint(
    password_hash: str,
) -> str:
    return hmac.new(
        AUTH_SECRET_KEY.encode(
            "utf-8"
        ),
        password_hash.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).hexdigest()


def create_password_reset_token(
    user_uid: str,
    password_hash: str,
) -> tuple[str, int]:
    expires_in = (
        PASSWORD_RESET_TOKEN_MINUTES
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
        "type":
            PASSWORD_RESET_TOKEN_TYPE,
        "iss": TOKEN_ISSUER,
        "iat": issued_at,
        "exp": expires_at,
        "jti": uuid.uuid4().hex,
        "pwd": (
            _password_hash_fingerprint(
                password_hash
            )
        ),
    }

    token = jwt.encode(
        payload,
        AUTH_SECRET_KEY,
        algorithm=AUTH_ALGORITHM,
    )

    return token, expires_in


def decode_password_reset_token(
    token: str,
) -> tuple[str, str] | None:
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
                    "pwd",
                ],
            },
        )
    except InvalidTokenError:
        return None

    if (
        payload.get("type")
        != PASSWORD_RESET_TOKEN_TYPE
    ):
        return None

    user_uid = payload.get("sub")
    fingerprint = payload.get("pwd")

    if not isinstance(
        user_uid,
        str,
    ):
        return None

    if not isinstance(
        fingerprint,
        str,
    ):
        return None

    cleaned_uid = user_uid.strip()
    cleaned_fingerprint = (
        fingerprint.strip()
    )

    if (
        not cleaned_uid
        or not cleaned_fingerprint
    ):
        return None

    return (
        cleaned_uid,
        cleaned_fingerprint,
    )


def password_reset_token_matches_hash(
    fingerprint: str,
    password_hash: str,
) -> bool:
    expected = (
        _password_hash_fingerprint(
            password_hash
        )
    )

    return hmac.compare_digest(
        fingerprint,
        expected,
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