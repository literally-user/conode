import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final, NewType
from uuid import UUID

from conode.domain.shared import Entity, ValueObject
from conode.domain.user.errors import (
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

MIN_ALLOWED_LAST_LENGTH: Final = 1
MAX_ALLOWED_LAST_LENGTH: Final = 30


class UserSystemRole(StrEnum):
    USER = "USER"
    ADMIN = "ADMIN"


class Username(ValueObject[str]):
    def __init__(self, value: str) -> None:
        value = value.strip()

        if MIN_ALLOWED_USERNAME_LENGTH <= len(value) <= MAX_ALLOWED_USERNAME_LENGTH:
            raise InvalidUserUsernameFormatError(
                "Company name length must be between"
                f"{MIN_ALLOWED_USERNAME_LENGTH} and "
                f"{MAX_ALLOWED_USERNAME_LENGTH}",
                [{"key": "name", "value": value}],
            )

        if re.match(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)[A-Za-z\d]+$", value):
            raise InvalidUserUsernameFormatError(
                "Username must contain at least "
                "one uppercase characters, "
                "one number "
                "and cannot contain special symbols",
                [{"key": "username", "value": value}],
            )

        super().__init__(value)


class FirstName(ValueObject[str]):
    def __init__(self, value: str) -> None:
        value = value.strip()

        if MIN_ALLOWED_FIRST_NAME_LENGTH <= len(value) <= MAX_ALLOWED_FIRST_NAME_LENGTH:
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

        if MIN_ALLOWED_LAST_LENGTH <= len(value) <= MAX_ALLOWED_LAST_LENGTH:
            raise InvalidUserLastNameFormatError(
                "First name length must be between"
                f"{MIN_ALLOWED_LAST_LENGTH} and "
                f"{MAX_ALLOWED_LAST_LENGTH}",
                [{"key": "last_name", "value": value}],
            )

        super().__init__(value)


class Email(ValueObject[str]):
    def __init__(self, value: str) -> None:
        value = value.strip()

        if re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}$", value):
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
    bio: str
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
            bio=bio,
        )

    def update_profile(
        self, *, first_name: str, last_name: str, username: str, bio: str
    ) -> None:
        self.first_name = FirstName(first_name)
        self.last_name = LastName(last_name)
        self.username = Username(username)
        self.bio = bio

    def increment_revision(self) -> None:
        self.token_revision += 1
