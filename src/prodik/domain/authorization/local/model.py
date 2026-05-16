from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NewType, Self
from uuid import UUID

from prodik.domain.shared import Entity
from prodik.domain.user import User, UserId

LocalAuthorizationId = NewType("LocalAuthorizationId", UUID)


@dataclass
class LocalAuthorization(Entity[LocalAuthorizationId]):
    user_id: UserId
    password: str

    @classmethod
    def new(cls, id: LocalAuthorizationId, user: User, password: str) -> Self:
        now = datetime.now(UTC)
        return cls(
            id=id,
            user_id=user.id,
            password=password,
            created_at=now,
            updated_at=now,
        )

    def update_password(self, password: str) -> None:
        self.password = password
