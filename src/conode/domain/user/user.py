from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final, NewType
from uuid import UUID

from conode.domain.role import Role, RoleId
from conode.domain.shared import Entity, ValueObject
from conode.domain.user.errors import (
    UsernameCannotBeLongerThanError,
    UsernameCannotBeShorterThanError,
)

UserId = NewType("UserId", UUID)

MIN_USERNAME_LENGTH: Final = 5
MAX_USERNAME_LENGTH: Final = 30


class UserRole(StrEnum):
    USER = "USER"
    ADMIN = "ADMIN"


class Username(ValueObject[str]):
    def __init__(self, value: str) -> None:
        if len(value) < MIN_USERNAME_LENGTH:
            raise UsernameCannotBeShorterThanError(
                f"Username cannot be shorter than {MIN_USERNAME_LENGTH} symbols", None
            )
        if len(value) > MAX_USERNAME_LENGTH:
            raise UsernameCannotBeLongerThanError(
                f"Username cannot be longer than {MAX_USERNAME_LENGTH} symbols", None
            )

        super().__init__(value)


@dataclass(kw_only=True)
class User(Entity[UserId]):
    username: Username
    password: str


@dataclass
class UserGrant(Entity[UserId]):
    user_id: UserId
    role_id: RoleId

    @classmethod
    def new(cls, id: UserId, role: Role, user: User) -> "UserGrant":
        now = datetime.now(UTC)
        return UserGrant(
            id=id,
            user_id=user.id,
            role_id=role.id,
            created_at=now,
            updated_at=now,
        )
