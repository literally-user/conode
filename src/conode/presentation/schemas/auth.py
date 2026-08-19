from typing import Annotated, Final

from pydantic import BaseModel, EmailStr, Field

from conode.domain.user.model import (
    MAX_ALLOWED_BIO_LENGTH,
    MAX_ALLOWED_FIRST_NAME_LENGTH,
    MAX_ALLOWED_LAST_NAME_LENGTH,
    MAX_ALLOWED_USERNAME_LENGTH,
    MIN_ALLOWED_FIRST_NAME_LENGTH,
    MIN_ALLOWED_LAST_NAME_LENGTH,
    MIN_ALLOWED_USERNAME_LENGTH,
)

MAX_ALLOWED_PASSWORD_LENGTH: Final = 30
MIN_ALLOWED_PASSWORD_LENGTH: Final = 5


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
    bio: Annotated[str, Field(max_length=MAX_ALLOWED_BIO_LENGTH)]
    email: EmailStr
    password: Annotated[
        str,
        Field(
            min_length=MIN_ALLOWED_PASSWORD_LENGTH,
            max_length=MAX_ALLOWED_PASSWORD_LENGTH,
        ),
    ]


class LoginRequest(BaseModel):
    email: EmailStr
    password: Annotated[
        str,
        Field(
            min_length=MIN_ALLOWED_PASSWORD_LENGTH,
            max_length=MAX_ALLOWED_PASSWORD_LENGTH,
        ),
    ]


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AuthorizedResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
