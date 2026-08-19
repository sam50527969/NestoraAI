import re
from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


def normalize_email(
    value: str,
) -> str:
    email = str(value or "").strip().lower()

    if not EMAIL_PATTERN.fullmatch(email):
        raise ValueError(
            "A valid email address is required."
        )

    return email


class UserRegister(BaseModel):
    email: str = Field(
        min_length=5,
        max_length=254,
    )

    full_name: str = Field(
        min_length=2,
        max_length=120,
    )

    password: str = Field(
        min_length=12,
        max_length=128,
    )

    @field_validator("email")
    @classmethod
    def validate_email(
        cls,
        value: str,
    ) -> str:
        return normalize_email(value)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(
        cls,
        value: str,
    ) -> str:
        cleaned = value.strip()

        if len(cleaned) < 2:
            raise ValueError(
                "Full name must contain at "
                "least two characters."
            )

        return cleaned


class LoginRequest(BaseModel):
    email: str = Field(
        min_length=5,
        max_length=254,
    )

    password: str = Field(
        min_length=1,
        max_length=128,
    )

    @field_validator("email")
    @classmethod
    def validate_email(
        cls,
        value: str,
    ) -> str:
        return normalize_email(value)


class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    user_uid: str
    email: str
    full_name: str
    role: Literal[
        "admin",
        "user",
    ]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
    user: UserResponse