from typing import Annotated

from pydantic import BaseModel, EmailStr, Field

from prodik.domain.user.model import (
    MAX_ALLOWED_BIO_LENGTH,
    MAX_ALLOWED_FIRST_NAME_LENGTH,
    MAX_ALLOWED_LAST_NAME_LENGTH,
    MAX_ALLOWED_USERNAME_LENGTH,
    MIN_ALLOWED_FIRST_NAME_LENGTH,
    MIN_ALLOWED_LAST_NAME_LENGTH,
    MIN_ALLOWED_USERNAME_LENGTH,
)


class UpdateCurrentUserProfileRequest(BaseModel):
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
    bio: Annotated[str, Field(max_length=MAX_ALLOWED_BIO_LENGTH)]


class UpdateCurrentUserPasswordRequest(BaseModel):
    old_password: Annotated[str, Field(min_length=7, max_length=100)]
    new_password: Annotated[str, Field(min_length=7, max_length=100)]
