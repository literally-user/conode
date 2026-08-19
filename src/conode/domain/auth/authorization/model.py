from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final, NewType, Self
from uuid import UUID

from conode.domain.auth.authorization.errors import (
    InvalidAuthorizationPasswordFormatError,
)
from conode.domain.shared import Entity, ValueObject
from conode.domain.user import User, UserId

AuthorizationId = NewType("AuthorizationId", UUID)

MAX_HASHED_PASSWORD_ALLOWED_LENGTH: Final = 30
MIN_HASHED_PASSWORD_ALLOWED_LENGTH: Final = 5


class HashedPassword(ValueObject[str]):
    def __init__(self, value: str) -> None:
        if (
            MIN_HASHED_PASSWORD_ALLOWED_LENGTH
            >= len(value)
            >= MAX_HASHED_PASSWORD_ALLOWED_LENGTH
        ):
            raise InvalidAuthorizationPasswordFormatError(
                "Company description length must be between"
                f"{MAX_HASHED_PASSWORD_ALLOWED_LENGTH} and "
                f"{MIN_HASHED_PASSWORD_ALLOWED_LENGTH}",
                [{"key": "password", "value": value}],
            )
        super().__init__(value)


@dataclass
class Authorization(Entity[AuthorizationId]):
    hashed_password: HashedPassword
    user_id: UserId

    @classmethod
    def new(
        cls, authorization_id: AuthorizationId, hashed_password: str, user: User
    ) -> Self:
        now = datetime.now(UTC)
        return cls(
            id=authorization_id,
            hashed_password=HashedPassword(hashed_password),
            user_id=user.id,
            created_at=now,
            updated_at=now,
        )
