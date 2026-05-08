import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final, NewType
from uuid import UUID

from prodik.domain.shared import Entity, ValueObject
from prodik.domain.user.errors import (
    InvalidUserEmailFormatError,
    InvalidUserFirstNameFormatError,
    InvalidUserLastNameFormatError,
    InvalidUserUsernameFormatError,
)

UserId = NewType("UserId", UUID)

MIN_ALLOWED_USERNAME_LENGTH: Final = 5
MAX_ALLOWED_USERNAME_LENGTH: Final = 30

MIN_ALLOWED_FIRST_NAME_LENGTH: Final = 1
MAX_ALLOWED_FIRST_NAME_LENGTH: Final = 30

MIN_ALLOWED_LAST_NAME_LENGTH: Final = 1
MAX_ALLOWED_LAST_NAME_LENGTH: Final = 30

MAX_ALLOWED_BIO_LENGTH: Final = 300


class UserSystemRole(StrEnum):
    USER = "USER"
    ADMIN = "ADMIN"


class Username(ValueObject[str]):
    def __init__(self, value: str) -> None:
        value = value.strip()

        if not (
            MIN_ALLOWED_USERNAME_LENGTH <= len(value) <= MAX_ALLOWED_USERNAME_LENGTH
        ):
            raise InvalidUserUsernameFormatError(
                "Company name length must be between"
                f"{MIN_ALLOWED_USERNAME_LENGTH} and "
                f"{MAX_ALLOWED_USERNAME_LENGTH}",
                [{"key": "name", "value": value}],
            )

        super().__init__(value)


class FirstName(ValueObject[str]):
    def __init__(self, value: str) -> None:
        value = value.strip()

        if not (
            MIN_ALLOWED_FIRST_NAME_LENGTH <= len(value) <= MAX_ALLOWED_FIRST_NAME_LENGTH
        ):
            raise InvalidUserFirstNameFormatError(
                "First name length must be between"
                f"{MIN_ALLOWED_FIRST_NAME_LENGTH} and "
                f"{MAX_ALLOWED_FIRST_NAME_LENGTH}",
                [{"key": "first_name", "value": value}],
            )

        super().__init__(value)


class LastName(ValueObject[str]):
    def __init__(self, value: str) -> None:
        value = value.strip()

        if not (
            MIN_ALLOWED_LAST_NAME_LENGTH <= len(value) <= MAX_ALLOWED_LAST_NAME_LENGTH
        ):
            raise InvalidUserLastNameFormatError(
                "First name length must be between"
                f"{MIN_ALLOWED_LAST_NAME_LENGTH} and "
                f"{MAX_ALLOWED_LAST_NAME_LENGTH}",
                [{"key": "last_name", "value": value}],
            )

        super().__init__(value)


class Bio(ValueObject[str]):
    def __init__(self, value: str) -> None:
        value = value.strip()

        if len(value) >= MAX_ALLOWED_BIO_LENGTH:
            raise InvalidUserLastNameFormatError(
                f"Bio length cannot be longer than {MAX_ALLOWED_BIO_LENGTH}",
                [{"key": "bio", "value": value}],
            )

        super().__init__(value)


class Email(ValueObject[str]):
    def __init__(self, value: str) -> None:
        value = value.strip()

        if not re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}$", value):
            raise InvalidUserEmailFormatError(
                "Invalid email format", [{"key": "email", "value": value}]
            )

        super().__init__(value)


@dataclass(kw_only=True)
class User(Entity[UserId]):
    system_role: UserSystemRole
    first_name: FirstName
    last_name: LastName
    username: Username
    email: Email
    bio: Bio
    token_revision: int

    @classmethod
    def new(
        cls,
        id: UserId,
        first_name: str,
        last_name: str,
        username: str,
        email: str,
        bio: str,
    ) -> "User":
        now = datetime.now(UTC)
        return User(
            id=id,
            first_name=FirstName(first_name),
            last_name=LastName(last_name),
            username=Username(username),
            email=Email(email),
            system_role=UserSystemRole.USER,
            created_at=now,
            updated_at=now,
            token_revision=1,
            bio=Bio(bio),
        )

    def update_profile(
        self, *, first_name: str, last_name: str, username: str, bio: str, email: str
    ) -> None:
        self.first_name = FirstName(first_name)
        self.last_name = LastName(last_name)
        self.username = Username(username)
        self.email = Email(email)
        self.bio = Bio(bio)

    def increment_revision(self) -> None:
        self.token_revision += 1

    def is_admin(self) -> bool:
        return self.system_role == UserSystemRole.ADMIN
