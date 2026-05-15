from typing import Annotated

from pydantic import BaseModel, EmailStr, Field

from prodik.domain.user.model import (
    MAX_ALLOWED_FIRST_NAME_LENGTH,
    MAX_ALLOWED_LAST_NAME_LENGTH,
    MAX_ALLOWED_USERNAME_LENGTH,
    MIN_ALLOWED_FIRST_NAME_LENGTH,
    MIN_ALLOWED_LAST_NAME_LENGTH,
    MIN_ALLOWED_USERNAME_LENGTH,
)


class RegisterRequest(BaseModel):
    username: Annotated[
        str,
        Field(
            min_length=MIN_ALLOWED_USERNAME_LENGTH,
            max_length=MAX_ALLOWED_USERNAME_LENGTH,
        ),
    ]
    first_name: Annotated[
        str,
        Field(
            min_length=MIN_ALLOWED_FIRST_NAME_LENGTH,
            max_length=MAX_ALLOWED_FIRST_NAME_LENGTH,
        ),
    ]
    last_name: Annotated[
        str,
        Field(
            min_length=MIN_ALLOWED_LAST_NAME_LENGTH,
            max_length=MAX_ALLOWED_LAST_NAME_LENGTH,
        ),
    ]
    password: Annotated[str, Field(min_length=7, max_length=100)]
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str
